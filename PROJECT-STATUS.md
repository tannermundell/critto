# Critto — Project Status

_Snapshot: early July 2026._

## Live / done
- **Supabase** (your project): `species` (150, seeded) + `sightings`; RLS; private storage bucket.
  Gamification populated (`db/02_gamification.sql`): `rarity` (blended — observation frequency AND an
  IUCN conservation floor, so threatened species can't read as Common), `introduced` (House Sparrow,
  Eastern Gray Squirrel).
- **Frontend** (Lovable, on your own Supabase): auth; Identify (upload → candidates → confirm); result
  card (About summary, "Listen" read-aloud, Introduced badge, hides "Not documented"); Collection
  (rarity cards, locked cards show name + rarity); **Journal**; Badges (Big Five, Endangered Guardian,
  class masters); desktop-responsive.
- **Mock API** on Render (`https://critto-mock.onrender.com`): `/identify` = mock; `/entry` = real agent
  (Wikipedia + IUCN + citations), currently `agent-fallback` until an LLM key is set.
- **Real GPU server** (`inference/gpu_server.py`): **validated on the AMD Instinct GPU** in the ROCm
  notebook — BioCLIP `/identify` returns real IDs (Lion at **99.95%**), `device: cuda`, `hip: 7.2`.
  Same contract as the mock. Not persistently hosted (the notebook is ephemeral + locked-down network).
- **GitHub** (public): `github.com/tannermundell/critto`.

## Key decision — no live hosting required
AMD support confirmed: **the project does not need to be hosted live** — a recorded demo is fine (the
guide lists a live URL as optional anyway). So the persistent Developer Cloud VM is **off the critical
path**. AMD-compute usage is evidenced by (a) the model running on the AMD GPU in the notebook (shown in
the video), and (b) Fireworks (AMD-hosted) for the LLM. Repo + slides document it for the auto pre-screen.

## Still to do
1. **Wire Fireworks** on Render (`LLM_*` env vars) → real `/entry` content + AMD compute in the live
   pipeline. ($6 Fireworks trial is enough; $50 hackathon credits pending.)
2. **Demo video** — show the Critto app end-to-end AND a few seconds of `gpu_server.py` running on the
   AMD GPU (the `/health` + Lion 99.95%).
3. **Slide deck (PDF)** — state AMD usage clearly (pre-screened).
4. **README "AMD compute" section** (pre-screened).
5. For real IDs in the video without a hosted URL: run `gpu_server.py` on your **laptop** + a tunnel
   (ngrok/cloudflared work fine off your machine), point Lovable at it while recording.

## Accounts / credits
- Fireworks: account created (same email); **$6 trial** available; **$50 hackathon credits pending**
  (allocated from July 7 for late sign-ups). Own Fireworks key works for Track 3.
- AMD Developer Cloud VM: signed up, **no credits yet**; not needed per the decision above.
- AMD ROCm notebooks: working (team-823), 4h/24h quota — use for validation, not hosting.

## Map of the project
- `PROJECT-STATUS.md` (this) · `NEXT-SESSION.md` · `Track3-Submission-Checklist.md`
- `Animal-ID-Build-Scope.md` · `Phase1-Architecture-Requirements.md` · `GPU-Window-Plan.md` · `ROADMAP.md`
- `Competitive-Analysis-Seek.md`
- `db/` (schema, 02_gamification, README) · `inference/` (main.py mock, gpu_server.py, agent.py, Dockerfiles)
- `scripts/` (species pull + enrich + CSV) · `gpu/vision_validate.py`
- `Lovable-Build-Prompt.md` + `lovable-prompts.md` · `assets/critto-cover.svg`
