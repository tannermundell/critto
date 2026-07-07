"""
Critto — vision identification via a Fireworks vision-language model (AMD-hosted).

Lets the LIVE app identify species without a self-hosted GPU: send the photo plus
our 150-species catalog to a Fireworks VLM (e.g. Minimax M3) and have it pick the
top-3 from the list. Runs on AMD hardware (Fireworks), so it keeps the whole live
pipeline on AMD. BioCLIP on the AMD GPU remains the validated high-accuracy path.

Reuses the same env as the agent; set VISION_MODEL to override the model used here.
"""

import json
import os
from typing import List, Optional

import requests

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.fireworks.ai/inference/v1").rstrip("/")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
VISION_MODEL = os.environ.get("VISION_MODEL") or os.environ.get("LLM_MODEL", "")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Critto-vision-fw/1.0"})


def _extract_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        pass
    for open_c, close_c in (("[", "]"), ("{", "}")):
        i, j = text.find(open_c), text.rfind(close_c)
        if i != -1 and j > i:
            try:
                return json.loads(text[i:j + 1])
            except Exception:
                continue
    return None


def identify(image_url: str, species: List[dict], topk: int = 3) -> Optional[List[dict]]:
    """Return up to `topk` candidate species dicts, or None on failure/no-key."""
    if not LLM_API_KEY or not VISION_MODEL or not image_url:
        return None

    catalog = "\n".join(
        f"{i}. {s['common_name']} ({s['scientific_name']})" for i, s in enumerate(species))
    prompt = (
        "Identify the South African animal (bird, mammal, or reptile) in this photo. "
        f"Choose the {topk} most likely species from the numbered list below ONLY. "
        "Return ONLY a JSON array of objects with keys 'index' (the list number) and "
        "'confidence' (0-1, most likely first, summing to <= 1).\n\n" + catalog
    )
    payload = {
        "model": VISION_MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]}],
        "temperature": 0.0,
    }
    try:
        r = SESSION.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
            json=payload, timeout=60,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        data = _extract_json(content)
        if not isinstance(data, list):
            return None
        out = []
        for item in data[:topk]:
            try:
                idx = int(item["index"])
                conf = float(item.get("confidence", 0))
            except (KeyError, ValueError, TypeError):
                continue
            if 0 <= idx < len(species):
                s = species[idx]
                out.append({
                    "common_name": s["common_name"],
                    "scientific_name": s["scientific_name"],
                    "class": s.get("class", ""),
                    "confidence": round(conf, 4),
                    "photo_url": s.get("photo_url", ""),
                })
        return out or None
    except Exception:
        return None
