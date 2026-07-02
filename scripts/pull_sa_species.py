#!/usr/bin/env python3
"""
Pull a ranked South African species list (birds, mammals, reptiles) from iNaturalist.

Why iNaturalist instead of GBIF for this:
- Ranks species by research-grade observations in South Africa, so the common /
  iconic species float to the top (same goal as before).
- Clean, human-curated English common names. (GBIF's vernacular names are full of
  banding codes like "LADO" and junk nicknames like "Flying Vuvuzela".)
- Correct reptile coverage. (GBIF's backbone has no clean "Reptilia" class, so the
  lookup silently fell back to all chordates = a duplicate bird list.)
- Bonus: a reference photo URL per species, useful for the cards and the model later.

Output: sa_species_list.csv with one row per species:
    class, common_name, scientific_name, conservation_status,
    inat_taxon_id, sa_observations, photo_url

Note: conservation_status here is iNaturalist's field and is sometimes blank.
True IUCN Red List status can be enriched later via GBIF if needed.

Dependency: requests   ->   pip install requests
Usage:
    py pull_sa_species.py            # ~50 per class (~150 total)
    py pull_sa_species.py --per 40   # custom count per class
"""

import argparse
import csv
import sys
import time
import requests

INAT = "https://api.inaturalist.org/v1"
CLASSES = ["Aves", "Mammalia", "Reptilia"]  # iNaturalist iconic taxa
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Critto-speciespull/2.0 (hackathon)"})


def get(url, params=None):
    for attempt in range(4):
        r = SESSION.get(url, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        time.sleep(1 + attempt)
    r.raise_for_status()


def resolve_place_id():
    """Find iNaturalist's place_id for South Africa (country level)."""
    data = get(f"{INAT}/places/autocomplete", {"q": "South Africa"})
    results = data.get("results", [])
    for r in results:
        if r.get("name") == "South Africa" and r.get("admin_level") == 0:
            return r["id"]
    if results:
        return results[0]["id"]
    sys.exit("Could not resolve South Africa place_id from iNaturalist")


def top_species(place_id, iconic, per):
    """Top species in SA for an iconic taxon, ranked by research-grade obs count."""
    # over-fetch a little so we can drop non-species rows and still hit `per`
    data = get(f"{INAT}/observations/species_counts", {
        "place_id": place_id,
        "iconic_taxa": iconic,
        "quality_grade": "research",
        "per_page": per + 15,
    })
    out = []
    for item in data.get("results", []):
        t = item.get("taxon") or {}
        if t.get("rank") != "species":
            continue  # skip genus/subspecies aggregates
        out.append((item, t))
        if len(out) >= per:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=50, help="species per class")
    ap.add_argument("--out", default="sa_species_list.csv")
    args = ap.parse_args()

    place_id = resolve_place_id()
    print(f"South Africa place_id = {place_id}", file=sys.stderr)

    rows = []
    for iconic in CLASSES:
        print(f"Pulling top {args.per} {iconic}...", file=sys.stderr)
        for item, t in top_species(place_id, iconic, args.per):
            photo = (t.get("default_photo") or {}).get("medium_url", "")
            cons = (t.get("conservation_status") or {}).get("status_name", "")
            rows.append({
                "class": iconic,
                "common_name": t.get("preferred_common_name", ""),
                "scientific_name": t.get("name", ""),
                "conservation_status": cons,
                "inat_taxon_id": t.get("id", ""),
                "sa_observations": item.get("count", ""),
                "photo_url": photo,
            })
        time.sleep(0.5)  # be polite to the API
        print(f"  done {iconic}", file=sys.stderr)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "class", "common_name", "scientific_name", "conservation_status",
            "inat_taxon_id", "sa_observations", "photo_url"])
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} species to {args.out}")


if __name__ == "__main__":
    main()
