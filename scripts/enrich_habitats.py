#!/usr/bin/env python3
"""
Critto — habitat/area tagging enrichment (writes directly to Supabase).

For each species it assigns 1-3 South African habitat tags from a fixed controlled
vocabulary (via a Fireworks LLM), then UPDATEs the `habitats` column in Supabase.
Powers the Explore "area" filter and adds learnable info.

First run db/03_habitats.sql (adds the habitats column).

Env vars:
  SUPABASE_URL          e.g. https://xxxx.supabase.co
  SUPABASE_SERVICE_KEY  Supabase service_role key (Project Settings -> API).
                        Server-side only; bypasses RLS. NEVER commit it.
  LLM_BASE_URL          default https://api.fireworks.ai/inference/v1
  LLM_API_KEY           Fireworks API key
  LLM_MODEL             Fireworks model id (e.g. your Minimax M3 model)

Usage:  pip install requests  ;  python enrich_habitats.py
"""

import json
import os
import time

import requests

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.fireworks.ai/inference/v1").rstrip("/")
LLM_API_KEY = os.environ["LLM_API_KEY"]
LLM_MODEL = os.environ["LLM_MODEL"]

VOCAB = ["Savanna/Bushveld", "Grassland", "Forest", "Fynbos/Shrubland", "Karoo/Semi-desert",
         "Wetland/Rivers", "Coastal/Marine", "Mountains", "Urban/Gardens"]

SB = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}", "Content-Type": "application/json"}
S = requests.Session()


def fetch_species():
    r = S.get(f"{SUPABASE_URL}/rest/v1/species",
              params={"select": "id,common_name,scientific_name,class"},
              headers=SB, timeout=30)
    r.raise_for_status()
    return r.json()


def _extract_json(text):
    try:
        return json.loads(text)
    except Exception:
        i, j = text.find("{"), text.rfind("}")
        return json.loads(text[i:j + 1]) if i != -1 and j > i else {}


def tag_batch(batch):
    listing = "\n".join(f"- {s['common_name']} ({s['scientific_name']}), {s['class']}" for s in batch)
    system = (
        "You are a South African wildlife habitat classifier. For each species, assign 1-3 tags "
        "for where it is found in South Africa. Use ONLY these exact tags: " + ", ".join(VOCAB) +
        ". Return ONLY a JSON object mapping each species' scientific name to an array of its tags."
    )
    payload = {"model": LLM_MODEL, "temperature": 0,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": listing}]}
    r = S.post(f"{LLM_BASE_URL}/chat/completions",
               headers={"Authorization": f"Bearer {LLM_API_KEY}"}, json=payload, timeout=90)
    r.raise_for_status()
    return _extract_json(r.json()["choices"][0]["message"]["content"])


def update_species(sid, tags):
    r = S.patch(f"{SUPABASE_URL}/rest/v1/species", params={"id": f"eq.{sid}"},
                headers={**SB, "Prefer": "return=minimal"}, json={"habitats": tags}, timeout=30)
    r.raise_for_status()


def main():
    species = fetch_species()
    print(f"{len(species)} species fetched from Supabase.")
    by_sci = {s["scientific_name"]: s for s in species}
    updated = 0
    BATCH = 25
    for k in range(0, len(species), BATCH):
        batch = species[k:k + BATCH]
        try:
            tags_map = tag_batch(batch)
        except Exception as e:
            print("  batch error:", e); continue
        for sci, tags in tags_map.items():
            s = by_sci.get(sci)
            if not s or not isinstance(tags, list):
                continue
            tags = [t for t in tags if t in VOCAB][:3] or ["Savanna/Bushveld"]
            update_species(s["id"], tags)
            updated += 1
            print(f"  {s['common_name']:28s} -> {tags}")
        time.sleep(0.3)
    print(f"\nDone. Updated {updated}/{len(species)} species in Supabase.")


if __name__ == "__main__":
    main()
