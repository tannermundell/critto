"""
Critto — mock inference API.

Stands in for the real GPU model server during pre-GPU development. It returns
responses in the EXACT shape the real server will use, so the frontend and agent
can be built and demoed now. When the real vision model is ready (on the AMD GPU),
it drops into the same `/identify` contract and nothing downstream changes.

Endpoints:
  GET  /health      -> liveness check
  POST /identify    -> top-N candidate species for an image (mock: random, plausible)
  POST /entry       -> structured field-guide entry for a species (mock: templated)

Run locally:
  pip install -r requirements.txt
  uvicorn main:app --reload --port 8000
  Then open http://localhost:8000/docs for interactive testing.
"""

import csv
import math
import os
import random
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Load the species list once at startup.
# Looks at SPECIES_CSV env var first, then a few sensible default locations.
# --------------------------------------------------------------------------
def _find_csv() -> Optional[Path]:
    candidates = [
        os.environ.get("SPECIES_CSV"),
        "sa_species_list.csv",
        "data/sa_species_list.csv",
        "../scripts/sa_species_list.csv",
    ]
    for c in candidates:
        if c and Path(c).is_file():
            return Path(c)
    return None


def _load_species() -> List[dict]:
    path = _find_csv()
    if not path:
        # Fall back to a tiny built-in set so the API still runs anywhere.
        return [
            {"class": "Aves", "common_name": "African Penguin",
             "scientific_name": "Spheniscus demersus",
             "iucn_status": "Critically Endangered", "photo_url": ""},
            {"class": "Mammalia", "common_name": "Lion",
             "scientific_name": "Panthera leo", "iucn_status": "Vulnerable", "photo_url": ""},
            {"class": "Reptilia", "common_name": "Puff Adder",
             "scientific_name": "Bitis arietans", "iucn_status": "Least Concern", "photo_url": ""},
        ]
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


SPECIES = _load_species()
SPECIES_BY_NAME = {s["scientific_name"]: s for s in SPECIES}


# --------------------------------------------------------------------------
# API setup
# --------------------------------------------------------------------------
app = FastAPI(title="Critto — Mock Inference API", version="mock-1")

# CORS: the Lovable frontend runs in a browser, so it must be allowed to call
# this API from a different origin. Open for the mock; tighten for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Request / response schemas (these define the contract the real server keeps).
# `class` is a reserved word in Python, so the field is `class_` internally but
# is aliased to "class" in the JSON the frontend sees.
# --------------------------------------------------------------------------
class IdentifyRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    image_url: Optional[str] = None              # real server uses this; mock ignores it
    class_: Optional[str] = Field(default=None, alias="class")  # optional hint, e.g. "Aves"


class Candidate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    common_name: str
    scientific_name: str
    class_: str = Field(alias="class")
    confidence: float
    photo_url: str = ""


class IdentifyResponse(BaseModel):
    candidates: List[Candidate]
    model_version: str = "mock-1"


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
    habitat: str
    diet: str
    size: str
    range: str
    where_to_spot: str
    fun_fact: str
    sources: List[str]
    model_version: str = "mock-1"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _softmax_confidences() -> List[float]:
    """Three descending confidences that look like a real classifier output."""
    raw = sorted([random.uniform(2.5, 5.0)] + [random.uniform(0.0, 2.0) for _ in range(2)],
                 reverse=True)
    exps = [math.exp(v) for v in raw]
    total = sum(exps)
    return [round(e / total, 4) for e in exps]


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "species_loaded": len(SPECIES), "model_version": "mock-1"}


@app.post("/identify", response_model=IdentifyResponse, response_model_by_alias=True)
def identify(req: IdentifyRequest):
    """Mock: return 3 random species (optionally biased to a class) with
    plausible, descending confidence scores."""
    pool = [s for s in SPECIES if not req.class_ or s.get("class") == req.class_] or SPECIES
    picks = random.sample(pool, k=min(3, len(pool)))
    confs = _softmax_confidences()
    candidates = [
        Candidate(
            common_name=p.get("common_name", ""),
            scientific_name=p.get("scientific_name", ""),
            class_=p.get("class", ""),
            confidence=confs[i],
            photo_url=p.get("photo_url", ""),
        )
        for i, p in enumerate(picks)
    ]
    return IdentifyResponse(candidates=candidates)


@app.post("/entry", response_model=EntryResponse, response_model_by_alias=True)
def entry(req: EntryRequest):
    """Mock: return a structured, templated field-guide entry. The real server
    will replace the placeholder text with a grounded, Fireworks-generated entry."""
    sci = req.species.scientific_name
    known = SPECIES_BY_NAME.get(sci, {})
    common = req.species.common_name or known.get("common_name", "This species")
    klass = req.species.class_ or known.get("class", "animal")
    status = known.get("iucn_status", "Not Evaluated")

    return EntryResponse(
        common_name=common,
        scientific_name=sci,
        iucn_status=status,
        habitat=f"[mock] Typical habitats where the {common} is found across South Africa.",
        diet=f"[mock] What the {common} ({klass}) usually eats.",
        size=f"[mock] Typical size and weight range for the {common}.",
        range=f"[mock] The {common}'s distribution within South Africa.",
        where_to_spot=f"[mock] Regions and parks where you're most likely to see a {common}.",
        fun_fact=f"[mock] A memorable fact about the {common}.",
        sources=["mock://placeholder"],
    )
