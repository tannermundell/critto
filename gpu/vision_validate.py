#!/usr/bin/env python3
"""
Critto — vision model validation on the AMD GPU (ROCm).

Run this in your AMD AI Notebook session to confirm three things at once:
  1) PyTorch sees the AMD GPU (ROCm),
  2) BioCLIP loads and runs on it,
  3) zero-shot classification over our 150 SA species works on a real image.

This is the Day-1 de-risk AND the first real `/identify` prototype (replaces the
random mock). BioCLIP is a CLIP model trained on the tree of life, so it can do
zero-shot species ID by comparing the image to our species-name text prompts.

Usage (in the notebook terminal). We fetch via the jsDelivr CDN because the shared
notebook IP gets rate-limited (HTTP 429) by raw.githubusercontent.com:
  wget https://cdn.jsdelivr.net/gh/tannermundell/critto@main/gpu/vision_validate.py
  python vision_validate.py                       # tests on a default lion photo
  python vision_validate.py --image <url-or-path> # test your own image
"""

import argparse
import csv
import io
import subprocess
import sys
import urllib.request


def _pip(*pkgs):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *pkgs])


# open_clip may not be in the base image; pillow usually is.
_pip("open_clip_torch", "pillow")

import torch                     # noqa: E402
import open_clip                 # noqa: E402
from PIL import Image            # noqa: E402

# jsDelivr CDN mirror of the repo (avoids raw.githubusercontent.com 429s on shared IPs)
SPECIES_CSV_URL = ("https://cdn.jsdelivr.net/gh/tannermundell/critto@main/"
                   "scripts/sa_species_list.csv")
DEFAULT_IMAGE = ("https://inaturalist-open-data.s3.amazonaws.com/"
                 "photos/9225318/medium.jpg")  # a lion


def load_species():
    with urllib.request.urlopen(SPECIES_CSV_URL) as r:
        text = r.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def load_image(src):
    if src.startswith("http"):
        with urllib.request.urlopen(src) as r:
            data = r.read()
        return Image.open(io.BytesIO(data)).convert("RGB")
    return Image.open(src).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", default=DEFAULT_IMAGE)
    ap.add_argument("--topk", type=int, default=5)
    args = ap.parse_args()

    # 1) GPU check
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"PyTorch {torch.__version__} | device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("WARNING: no GPU visible — running on CPU (check the ROCm environment).")

    # 2) Load BioCLIP
    print("Loading BioCLIP (first run downloads weights) ...")
    model, _, preprocess = open_clip.create_model_and_transforms(
        "hf-hub:imageomics/bioclip")
    tokenizer = open_clip.get_tokenizer("hf-hub:imageomics/bioclip")
    model = model.to(device).eval()

    # 3) Encode our species labels once
    species = load_species()
    sci = [s["scientific_name"] for s in species]
    common = [s["common_name"] for s in species]
    prompts = [f"a photo of {name}" for name in sci]

    print(f"Encoding {len(prompts)} species labels ...")
    with torch.no_grad():
        text = tokenizer(prompts).to(device)
        tfeat = model.encode_text(text)
        tfeat = tfeat / tfeat.norm(dim=-1, keepdim=True)

    # Classify the image
    print(f"Loading image: {args.image}")
    img = preprocess(load_image(args.image)).unsqueeze(0).to(device)
    with torch.no_grad():
        ifeat = model.encode_image(img)
        ifeat = ifeat / ifeat.norm(dim=-1, keepdim=True)
        probs = (ifeat @ tfeat.T).squeeze(0).softmax(dim=-1)

    topk = probs.topk(min(args.topk, len(species)))
    print("\nTop predictions:")
    for score, idx in zip(topk.values.tolist(), topk.indices.tolist()):
        print(f"  {common[idx]:30s} ({sci[idx]:28s})  {score * 100:5.1f}%")


if __name__ == "__main__":
    main()
