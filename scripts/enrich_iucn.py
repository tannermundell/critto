#!/usr/bin/env python3
"""
Enrich the SA species list with authoritative IUCN Red List status from GBIF.

Reads:  sa_species_list.csv  (output of pull_sa_species.py)
Writes: sa_species_list.csv  (in place — the conservation column is replaced
                              with a clean, normalised `iucn_status`)

For each species:
  1. Match the scientific name to a GBIF taxon key.
  2. Look up its IUCN Red List category.
  3. Normalise to title case (e.g. LEAST_CONCERN -> "Least Concern").
  4. If GBIF has no IUCN record, fall back to iNaturalist's value (title-cased).

Dependency: requests   ->   pip install requests
Usage:
    py enrich_iucn.py
    py enrich_iucn.py --in sa_species_list.csv --out sa_species_list.csv
"""

import argparse
import csv
import sys
import time
import requests

GBIF = "https://api.gbif.org/v1"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Critto-iucn-enrich/1.0 (hackathon)"})

# Manual overrides for species where iNaturalist's modern (renamed) scientific
# name doesn't link to the IUCN assessment filed under the older accepted name,
# so GBIF returns "Not Evaluated" / nothing. All verified Least Concern on the
# IUCN Red List under their previous names. Override wins over the GBIF lookup.
OVERRIDES = {
    "Icthyophaga vocifer": "Least Concern",        # African Fish-Eagle (Haliaeetus vocifer)
    "Chroicocephalus hartlaubii": "Least Concern", # Hartlaub's Gull
    "Ardea ibis": "Least Concern",                 # Western Cattle-Egret (Bubulcus ibis)
    "Lupulella mesomelas": "Least Concern",        # Black-backed Jackal (Canis mesomelas)
    "Cynictis penicillata": "Least Concern",       # Yellow Mongoose
    "Pelusios sinuatus": "Least Concern",          # Serrated Hinged Terrapin
    "Elaiophis inornatus": "Least Concern",        # Olive House Snake (Boaedon inornatus)
}


def get(url, params=None):
    for attempt in range(4):
        try:
            r = SESSION.get(url, params=params, timeout=30)
        except requests.RequestException:
            time.sleep(1 + attempt)
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 404:
            return None
        time.sleep(1 + attempt)
    return None


def titleise(s):
    """LEAST_CONCERN or 'least concern' -> 'Least Concern'."""
    if not s:
        return ""
    return s.replace("_", " ").strip().title()


def gbif_iucn(scientific_name):
    """Authoritative IUCN category for a scientific name, or '' if none."""
    match = get(f"{GBIF}/species/match",
                {"name": scientific_name, "rank": "SPECIES"})
    if not match:
        return ""
    key = match.get("usageKey")
    if not key:
        return ""
    data = get(f"{GBIF}/species/{key}/iucnRedListCategory")
    if not data:
        return ""
    return titleise(data.get("category", ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", default="sa_species_list.csv")
    ap.add_argument("--out", dest="outfile", default="sa_species_list.csv")
    args = ap.parse_args()

    with open(args.infile, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        sys.exit("Input CSV is empty.")

    fieldnames = ["class", "common_name", "scientific_name", "iucn_status",
                  "inat_taxon_id", "sa_observations", "photo_url"]

    gbif_hits = 0
    overrides_applied = 0
    inat_fallbacks = 0
    still_blank = 0

    for i, row in enumerate(rows, 1):
        sci = row.get("scientific_name", "").strip()
        if sci in OVERRIDES:
            status = OVERRIDES[sci]
            overrides_applied += 1
        else:
            status = gbif_iucn(sci) if sci else ""
            if status and status != "Not Evaluated":
                gbif_hits += 1
            else:
                # fall back to iNaturalist's value from the pull, if present
                fallback = titleise(row.get("conservation_status", ""))
                if fallback:
                    status = fallback
                    inat_fallbacks += 1
                elif not status:
                    still_blank += 1
        row["iucn_status"] = status
        print(f"  [{i}/{len(rows)}] {sci or '?'} -> {status or '(none)'}",
              file=sys.stderr)
        time.sleep(0.1)  # be polite to the API

    with open(args.outfile, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"\nDone. GBIF/IUCN hits: {gbif_hits} | overrides: {overrides_applied} | "
          f"iNat fallbacks: {inat_fallbacks} | still blank: {still_blank}")
    print(f"Wrote {len(rows)} rows to {args.outfile}")


if __name__ == "__main__":
    main()
