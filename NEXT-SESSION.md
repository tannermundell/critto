# Critto — next session

Big milestone hit: the real BioCLIP `/identify` runs on the AMD GPU (Lion 99.95%). Live hosting is
NOT required (AMD support confirmed) — so the VM is off the critical path. Focus shifts to Fireworks
and the submission assets.

## Tomorrow, in order
1. **Wire Fireworks** → real `/entry`.
   - Get your Fireworks API key (fw_...) + pick a model from their catalog.
   - On Render → service → Environment, add:
     `LLM_BASE_URL=https://api.fireworks.ai/inference/v1`
     `LLM_MODEL=accounts/fireworks/models/<model>`
     `LLM_API_KEY=<fireworks key>`
   - Render redeploys; test `/entry` → should return `agent-llm` with real fields.
2. **README: add an "AMD compute" section** (pre-screen reads the repo) — ROCm BioCLIP + Fireworks.
3. **Demo recording setup** — run `gpu_server.py` on your laptop + ngrok/cloudflared tunnel, point
   Lovable at it, so the app shows real IDs on camera. Also capture the notebook GPU run for the video.
4. **Start the slide deck (PDF)** — state AMD usage (pre-screened).

## Housekeeping
- **Push tonight's/local changes**: `git add . && git commit -m "docs + status" && git push`.
- Chase the $50 Fireworks hackathon credits in Discord if they haven't landed (works on the $6 trial meanwhile).
