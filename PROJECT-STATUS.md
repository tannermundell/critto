# Critto — Project Status

_Snapshot: 7 July 2026._

## The whole live app now runs on AMD
Both inference endpoints run on **AMD-hosted Fireworks** (model: Minimax M3), live on Render — no
self-hosted GPU, no VM. The hosting question is fully resolved.

- **`/identify`** — Fireworks **vision** model picks the top-3 from our 150 species (constrained to the
  list). Verified: Lion 98%. Falls back to the random mock only if the key/image is missing.
- **`/entry`** — Fireworks **LLM** writes grounded field-guide fields (Wikipedia + IUCN + citations).
  Verified: real habitat/diet/range/etc., `model_version: agent-llm`.
- **BioCLIP on the AMD Instinct GPU** (`inference/gpu_server.py`) — validated separately (Lion 99.95%,
  `device: cuda`, `hip: 7.2`). This is the high-accuracy classifier and the GPU-compute evidence for the
  demo video. AMD is demonstrated on two fronts: Instinct GPU (shown) + Fireworks (live).

## Live / done
- **Supabase**: 150 species seeded + gamification (`rarity` blended with IUCN floor; `introduced`).
- **Frontend** (Lovable, own Supabase): auth, Identify, result card (About, read-aloud, Introduced badge,
  hides "Not documented"), Collection (rarity cards), Journal, Badges, desktop-responsive. **Already
  pointed at the Render URL — so the live app now does real AI end to end.**
- **Inference** on Render (`critto-mock.onrender.com`): real `/identify` + `/entry` on Fireworks (above).
- **GitHub** (public): `github.com/tannermundell/critto`.

## Still to do (build is essentially done)
1. **Demo video** — Critto app end-to-end + a few seconds of BioCLIP on the AMD Instinct GPU.
2. **Slide deck (PDF)** — state AMD usage (pre-screened).
3. **README "AMD compute" section** (pre-screened) — Fireworks (live, both endpoints) + ROCm BioCLIP.
4. Optional polish: pre-generate + cache the 150 entries; reptile prompt tuning; more badge sets;
   multilingual names; laptop-served BioCLIP for the video's live-ID shots.

## Accounts / credits
- **Fireworks: $50 credits live**, own key, Minimax M3 (serverless, vision + text). Powers the live app.
  (The 5 Track-1 models are harness-only; Track 3 has no restriction.)
- AMD ROCm notebooks: working (team-823, 4h/24h) — used for BioCLIP validation.
- AMD Developer Cloud VM: not needed (no live GPU hosting required).

## Map of the project
- `PROJECT-STATUS.md` (this) · `NEXT-SESSION.md` · `Track3-Submission-Checklist.md`
- `Animal-ID-Build-Scope.md` · `Phase1-Architecture-Requirements.md` · `GPU-Window-Plan.md` · `ROADMAP.md`
- `Competitive-Analysis-Seek.md`
- `db/` · `inference/` (main.py = live server: Fireworks `/identify` + `/entry`; gpu_server.py = BioCLIP;
  agent.py; vision_fireworks.py) · `scripts/` · `gpu/vision_validate.py`
- `Lovable-Build-Prompt.md` + `lovable-prompts.md` · `assets/critto-cover.svg`
