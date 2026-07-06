"""
Critto — GPU inference server (the REAL one).

Same API contract as the mock (main.py), so the frontend swaps by changing one
base URL. Runs on an AMD GPU (a notebook session via a tunnel, or the AMD
Developer Cloud VM). One stable endpoint for everything, all on AMD:

  /identify  -> BioCLIP zero-shot over the SA species — runs on the AMD GPU (ROCm)
  /entry     -> knowledge agent (Wikipedia + IUCN + Fireworks LLM) — from agent.py
  /health    -> liveness + device info

Run:
  pip install -r requirements-gpu.txt
  pip install --no-deps open_clip_torch          # keep the ROCm torch
  export SPECIES_CSV=./sa_species_list.csv       # or ../scripts/sa_species_list.csv
  uvicorn gpu_server:app --host 0.0.0.0 --port 8000
"""

import csv
import io
import os
import urllib.request
from pathlib import Path
from typing import List, Optional

import open_clip
import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field

from agent import build_entry   # reuse the /entry knowledge agent


# --------------------------------------------------------------------------
# Species data
# --------------------------------------------------------------------------
def _find_csv() -> Path:
    for c in (os.environ.get("SPECIES_CSV"), "sa_species_list.csv",
              "../scripts/sa_species_list.csv"):
        if c and Path(c).is_file():
            return Path(c)
    raise SystemExit("species CSV not found — set SPECIES_CSV")


with open(_find_csv(), newline="", encoding="utf-8") as f:
    SPECIES = list(csv.DictReader(f))
SPECIES_BY_NAME = {s["scientific_name"]: s for s in SPECIES}


# --------------------------------------------------------------------------
# Load BioCLIP once and precompute the species text embeddings
# --------------------------------------------------------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL = "hf-hub:imageomics/bioclip"

print(f"Loading BioCLIP on {DEVICE} (hip={getattr(torch.version, 'hip', None)}) ...")
_model, _, _preprocess = open_clip.create_model_and_transforms(MODEL)
_tokenizer = open_clip.get_tokenizer(MODEL)
_model = _model.to(DEVICE).eval()

with torch.no_grad():
    _prompts = [f"a photo of {s['scientific_name']}" for s in SPECIES]
    _tfeat = _model.encode_text(_tokenizer(_prompts).to(DEVICE))
    _tfeat = _tfeat / _tfeat.norm(dim=-1, keepdim=True)
_logit_scale = _model.logit_scale.exp()
print(f"Ready: {len(SPECIES)} species encoded on {DEVICE}.")


# --------------------------------------------------------------------------
# Schemas (identical contract to the mock)
# --------------------------------------------------------------------------
class IdentifyRequest(BaseModel):
    image_url: str


class Candidate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    common_name: str
    scientific_name: str
    class_: str = Field(alias="class")
    confidence: float
    photo_url: str = ""


class IdentifyResponse(BaseModel):
    candidates: List[Candidate]
    model_version: str = "bioclip-1"


class SpeciesRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    common_name: str
    scientific_name: str
    class_: Optional[str] = Field(default=None, alias="class")


class EntryRequest(BaseModel):
    species: SpeciesRef


class EntryResponse(BaseModel):
    common_name: str
    scientific_name: str
    iucn_status: str
    summary: str = ""
    habitat: str
    diet: str
    size: str
    range: str
    where_to_spot: str
    fun_fact: str
    sources: List[str]
    model_version: str = "agent-1"


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------
app = FastAPI(title="Critto — GPU Inference", version="bioclip-1")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


def _load_image(url: str) -> Image.Image:
    data = urllib.request.urlopen(url, timeout=20).read()
    return Image.open(io.BytesIO(data)).convert("RGB")


@app.get("/health")
def health():
    return {"status": "ok", "device": DEVICE,
            "hip": getattr(torch.version, "hip", None),
            "species_loaded": len(SPECIES), "model_version": "bioclip-1"}


@app.post("/identify", response_model=IdentifyResponse, response_model_by_alias=True)
def identify(req: IdentifyRequest):
    img = _preprocess(_load_image(req.image_url)).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        ifeat = _model.encode_image(img)
        ifeat = ifeat / ifeat.norm(dim=-1, keepdim=True)
        probs = (_logit_scale * ifeat @ _tfeat.T).squeeze(0).softmax(dim=-1)
    top = probs.topk(3)
    candidates = []
    for score, idx in zip(top.values.tolist(), top.indices.tolist()):
        s = SPECIES[idx]
        candidates.append(Candidate(
            common_name=s["common_name"], scientific_name=s["scientific_name"],
            class_=s.get("class", ""), confidence=round(score, 4),
            photo_url=s.get("photo_url", "")))
    return IdentifyResponse(candidates=candidates)


@app.post("/entry", response_model=EntryResponse, response_model_by_alias=True)
def entry(req: EntryRequest):
    sci = req.species.scientific_name
    known = SPECIES_BY_NAME.get(sci, {})
    common = req.species.common_name or known.get("common_name", "This species")
    klass = req.species.class_ or known.get("class", "animal")
    status = known.get("iucn_status") or "Not Evaluated"
    data = build_entry(common, sci, klass)
    return EntryResponse(
        common_name=common, scientific_name=sci, iucn_status=status,
        summary=data["summary"], habitat=data["habitat"], diet=data["diet"],
        size=data["size"], range=data["range"], where_to_spot=data["where_to_spot"],
        fun_fact=data["fun_fact"], sources=data["sources"],
        model_version=data["model_version"])
