# Mock Inference API

Stand-in for the real GPU model server. Returns responses in the exact shape the
real server will use, so the frontend and agent can be built and demoed before the
GPU window. Later, the real vision model drops into the same `/identify` contract.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET  | `/health`   | Liveness check + how many species loaded |
| POST | `/identify` | Top-3 candidate species for an image (mock: random, plausible) |
| POST | `/entry`    | Structured field-guide entry for a species (mock: templated) |

Interactive docs (auto-generated): visit `/docs` on the running server.

### `/identify`
```
Request:  { "image_url": "https://.../photo.jpg" }      // image_url optional for the mock
Response: { "candidates": [
              { "common_name": "African Penguin", "scientific_name": "Spheniscus demersus",
                "class": "Aves", "confidence": 0.94, "photo_url": "..." },
              ... 2 more ...
            ],
            "model_version": "mock-1" }
```

### `/entry`
```
Request:  { "species": { "common_name": "African Penguin",
                         "scientific_name": "Spheniscus demersus", "class": "Aves" } }
Response: { "common_name": "...", "scientific_name": "...", "iucn_status": "Critically Endangered",
            "habitat": "...", "diet": "...", "size": "...", "range": "...",
            "where_to_spot": "...", "fun_fact": "...", "sources": ["..."], "model_version": "mock-1" }
```

## Run locally

```bash
pip install -r requirements.txt
# point it at the species list (or copy the CSV into this folder)
export SPECIES_CSV=../scripts/sa_species_list.csv     # Windows PowerShell: $env:SPECIES_CSV="..\scripts\sa_species_list.csv"
uvicorn main:app --reload --port 8000
```

Test it:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/identify -H "Content-Type: application/json" -d "{}"
```

## Run with Docker

```bash
# 1. put a copy of the species list next to the Dockerfile so it goes into the image
cp ../scripts/sa_species_list.csv .        # PowerShell: copy ..\scripts\sa_species_list.csv .
# 2. build and run
docker build -t wildlens-mock .
docker run -p 8000:8000 wildlens-mock
```

## Deploy (so Lovable can reach it)

Lovable runs in the browser/cloud, so the API needs a public URL. Easiest paths:

- **Render / Railway** — connect the repo, it builds the Dockerfile, gives you a URL like
  `https://wildlens-mock.onrender.com`.
- **Hugging Face Spaces (Docker)** — push this folder; you get a public Space URL.
- **Local + tunnel** — `uvicorn ...` then `ngrok http 8000` for a temporary public URL.

## How the frontend uses it

Store the base URL as one config value in Lovable (e.g. `API_BASE_URL`). All calls go to
`{API_BASE_URL}/identify` and `{API_BASE_URL}/entry`.

**The swap later:** when the real model server is live on AMD Developer Cloud during the GPU
window, change that one `API_BASE_URL` to the AMD endpoint. The contract is identical, so the
frontend doesn't change.

## /entry knowledge agent

`/entry` is a real agent (`agent.py`): it retrieves the Wikipedia article for the species and
combines it with the stored IUCN status. If an LLM is configured it writes the structured fields
(habitat, diet, size, range, where-to-spot, fun fact) grounded in that text; otherwise it returns
the real Wikipedia `summary` with honest "Not documented" placeholders. Responses are cached
in-memory per species. The response now includes a `summary` field (an "About" blurb).

The LLM is OpenAI-compatible, so the same code works with OpenAI now and Fireworks at kickoff —
set env vars (no code change):

```
# OpenAI (test now)
LLM_API_KEY=sk-...
# LLM_MODEL defaults to gpt-4o-mini, LLM_BASE_URL defaults to OpenAI

# Fireworks (at kickoff)
LLM_BASE_URL=https://api.fireworks.ai/inference/v1
LLM_MODEL=accounts/fireworks/models/<model-revealed-on-launch>
LLM_API_KEY=<fireworks key>
```

On Render, add these under the service's **Environment** tab; it redeploys automatically.

## Real GPU server (`gpu_server.py`)

`gpu_server.py` is the real inference service — same contract as the mock, so the frontend swaps by
changing one base URL. It serves both endpoints on an AMD GPU:
- `/identify` — **BioCLIP zero-shot** over the 150 species, running on the AMD GPU (ROCm). Text
  embeddings are precomputed once at startup; each request only encodes the image.
- `/entry` — the same knowledge agent as the mock (Wikipedia + IUCN + Fireworks LLM).
- `/health` — reports `device` and `hip` so you can confirm it's on the GPU.

### Run it directly on the AMD Developer Cloud VM (recommended)
The VM has ROCm + PyTorch preinstalled, so no Docker needed:
```bash
git clone https://github.com/tannermundell/critto && cd critto/inference
pip install -r requirements-gpu.txt
pip install --no-deps open_clip_torch          # keep the ROCm torch
export SPECIES_CSV=./sa_species_list.csv
export LLM_BASE_URL=https://api.fireworks.ai/inference/v1   # for /entry
export LLM_MODEL=accounts/fireworks/models/<model>
export LLM_API_KEY=<fireworks key>
uvicorn gpu_server:app --host 0.0.0.0 --port 8000
```

### Give it a public HTTPS URL (required — the frontend is HTTPS)
Browsers block an HTTPS page calling a plain-HTTP API. Easiest fix is a Cloudflare quick tunnel
(no signup, gives an https URL):
```bash
# in a second shell on the VM / notebook
cloudflared tunnel --url http://localhost:8000
```
Point Lovable's `API_BASE_URL` at the printed `https://...trycloudflare.com` URL. For a permanent
domain, use a Caddy reverse proxy instead.

### Testing from a notebook session first
Same steps in the notebook's terminal (uvicorn in one terminal, cloudflared in another). Note the
notebook is time-limited (4h/24h), so use it to validate; use the VM for the judging window.

### Docker (optional)
`Dockerfile.rocm` builds the same server on a ROCm base. Running directly on the VM is simpler and
avoids the large base image; the container is here for reproducibility.

### Cutover checklist
1. Server healthy on the VM (`/health` shows `device: cuda`, `hip` set).
2. Public HTTPS URL via cloudflared/Caddy.
3. Change `API_BASE_URL` in Lovable to that URL.
4. `/identify` now returns real BioCLIP predictions; `/entry` returns Fireworks-written entries.
