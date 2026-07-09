# Critto 🐾

**Identify South Africa's wildlife from a photo.**

Critto is a South African wildlife identification app. Snap or upload a photo of a bird, mammal, or
reptile and Critto identifies the species, then returns a rich, source-backed field-guide entry — wrapped
in a collection game (rarity cards, coins) designed to get people outdoors and connect them with nature.

Built for the **AMD Developer Hackathon: ACT II — Track 3 (Unicorn)**.

- **Live app:** _<add your Lovable URL>_
- **Demo video:** _<add link>_

---

## Built on AMD

AMD is used on **two fronts**:

1. **Inference via Fireworks AI — AMD's inference partner.** Both endpoints call **Minimax M3 on
   Fireworks AI**, accessed through the **AMD AI Developer Program** and powered by **AMD Instinct™ GPUs**
   (Fireworks runs on AMD Instinct alongside other hardware):
   - `/identify` — a Fireworks **vision** model identifies the animal, constrained to our 150-species catalog, and returns the top 3.
   - `/entry` — a Fireworks **LLM** writes the grounded field-guide fields (habitat, diet, range, etc.) from retrieved sources.
2. **BioCLIP on AMD Instinct GPUs (ROCm).** Our specialised zero-shot classifier is validated **directly**
   on AMD Instinct hardware via ROCm (`inference/gpu_server.py`, `gpu/vision_validate.py`) — e.g. 99.95% on
   a test image, `device: cuda`, `hip: 7.2`. This is the high-accuracy vision path.

---

## How it works

```
┌──────────────┐      ┌──────────────────┐      ┌────────────────────────────┐
│   Lovable    │      │    Supabase      │      │   Inference API (FastAPI)  │
│  (frontend)  │      │ (auth/data/store)│      │                            │
│ upload photo │──1──▶│                  │──2──▶│ /identify → Fireworks VLM  │  (AMD)
│ result card  │◀─────│                  │◀─3───│   → top-3 from 150 species │
│ collection   │──4──▶│ sightings        │      │ /entry → Fireworks LLM     │  (AMD)
│ + coins      │      │                  │◀─────│   → grounded field guide   │
└──────────────┘      └──────────────────┘      └────────────────────────────┘
                                                  BioCLIP on AMD Instinct GPU (ROCm)
                                                  = validated high-accuracy classifier
```

- **Frontend:** Lovable (React) web app — capture/upload, candidate selection, result card, a Collection
  (rarity cards derived from observation frequency + IUCN status), a personal Journal, and coins.
- **Backend data:** Supabase — auth, 150-species table, sightings, image storage (row-level security).
- **Inference API:** FastAPI (deployed on Render) — `/identify` and `/entry`, both via Fireworks AI (AMD partner).
- **Species data:** 150 curated South African species (birds/mammals/reptiles) pulled from iNaturalist,
  enriched with IUCN Red List status via GBIF.

---

## Repository structure

| Path | What |
|---|---|
| `inference/main.py` | Live API — Fireworks `/identify` (vision) + `/entry` (LLM) |
| `inference/agent.py` | Field-guide agent — Wikipedia + IUCN retrieval + LLM synthesis |
| `inference/vision_fireworks.py` | Fireworks vision-model identification |
| `inference/gpu_server.py` | BioCLIP `/identify` on AMD Instinct GPU (ROCm) |
| `gpu/vision_validate.py` | BioCLIP validation script for the AMD notebook |
| `db/` | Supabase schema, seeding, gamification SQL |
| `scripts/` | Species data pull (`pull_sa_species.py`) + IUCN enrichment (`enrich_iucn.py`) |
| `assets/` | Cover image |

---

## Setup & usage

### Prerequisites
- Python 3.11+
- A Supabase project, and a Fireworks AI API key

### 1. Database
Create the schema and seed the species (see `db/README.md`):
- Run `db/schema.sql` and `db/02_gamification.sql` in the Supabase SQL editor.
- Import `scripts/sa_species_list.csv` into the `species` table (150 rows).

### 2. Inference API (Fireworks — the live app)
```bash
cd inference
pip install -r requirements.txt
export LLM_BASE_URL=https://api.fireworks.ai/inference/v1
export LLM_MODEL=<your Fireworks model id, e.g. a Minimax M3 model>
export LLM_API_KEY=<your Fireworks API key>
export SPECIES_CSV=../scripts/sa_species_list.csv
uvicorn main:app --host 0.0.0.0 --port 8000
```
Endpoints: `GET /health`, `POST /identify` (`{"image_url": "..."}`), `POST /entry`
(`{"species": {"common_name","scientific_name","class"}}`). Interactive docs at `/docs`.
(On Windows PowerShell, set env vars with `$env:LLM_API_KEY="..."`.)

### 3. BioCLIP on an AMD GPU (ROCm) — high-accuracy path
On an AMD ROCm environment (PyTorch preinstalled):
```bash
cd inference
pip install -r requirements-gpu.txt
pip install --no-deps open_clip_torch      # keep the ROCm torch
export SPECIES_CSV=./sa_species_list.csv
uvicorn gpu_server:app --host 0.0.0.0 --port 8000
```
Or run `gpu/vision_validate.py` for a quick end-to-end validation. See `inference/README.md`.

### 4. Frontend
The Lovable app connects to your Supabase project and points its API base URL at the inference API above.

---

## Tech stack
AMD Instinct GPU (ROCm) · Fireworks AI (Minimax M3) · BioCLIP / OpenCLIP · FastAPI · Supabase ·
Lovable (React) · Render.

## Team
Aidan Dean & Tanner Mundell — AMD Developer Hackathon: ACT II, Track 3 (Unicorn).
