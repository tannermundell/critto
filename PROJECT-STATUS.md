# Critto — Project Status

_Snapshot at end of build session (early July 2026)._

## Live now
- **Supabase** (your project): `species` (150, seeded) + `sightings`; RLS; private `sightings`
  storage bucket. Gamification columns populated via `db/02_gamification.sql`:
  - `rarity` — Common → Legendary, ranked **within class**.
  - `introduced` — flagged for House Sparrow and Eastern Gray Squirrel.
- **Inference API** on Render — `https://critto-mock.onrender.com`:
  - `/identify` — **mock** (returns random species). Real BioCLIP vision model swaps in during the
    GPU window using the same contract (one URL change).
  - `/entry` — **real agent** (Wikipedia retrieval + IUCN status + citations). Currently
    `agent-fallback`: the About `summary` is real; the split fields say "Not documented" until an
    LLM key is set.
  - `/health` — ok, `species_loaded: 150`.
- **Frontend** (Lovable, connected to your own Supabase — not Lovable Cloud):
  - Auth; Identify (upload → candidates → confirm); Result card (About, "Listen" read-aloud,
    Introduced badge, hides "Not documented"); Collection (rarity cards, locked cards show name +
    rarity); **Journal** (renamed from My List).
- **GitHub** (public): `github.com/tannermundell/critto` — satisfies the submission repo requirement.

## One toggle from a big upgrade
Set `LLM_API_KEY` (+ optional `LLM_BASE_URL`, `LLM_MODEL`) in Render's Environment tab and `/entry`
fills real habitat/diet/size/range/where-to-spot/fun-fact. Works with OpenAI now, or Fireworks at
kickoff — no rebuild. See `inference/README.md` for the exact vars.

## Still to do
- **GPU window (the only true GPU work):** get BioCLIP running on ROCm; measure top-3 accuracy;
  swap the mock `/identify` for the real model. Fine-tune only if accuracy is weak.
- **LLM:** connect Fireworks (or OpenAI) so entries are fully written.
- **Assets:** fine-tune/eval images; demo photos; cover → PNG; video + slide deck for submission.
- **Gamification next:** badge/coin sets (Big Five, Endangered Guardians, class masters); levels/points.
- **UX:** ongoing polish from your brother's review.

## Key dates / credits (verify on the live page)
- Register by **2 July** for day-one hackathon credits ($50 Fireworks). Later sign-ups: from 7 July.
- New AMD AI Developer Program sign-ups: **$100 Cloud + $50 Fireworks** via a separate 2–3 day
  approval, **not** tied to the hackathon cutoff.
- GPU instance access details come at event start; treat the GPU window as the only true GPU time.

## Map of the project
- `PROJECT-STATUS.md` — this file (current state).
- `Animal-ID-Build-Scope.md` — product framing + phasing.
- `Phase1-Architecture-Requirements.md` — architecture & requirements.
- `GPU-Window-Plan.md` — what to build before vs during the GPU window.
- `ROADMAP.md` — future features (cards/badges, alien flag, sound, social).
- `db/` — `schema.sql`, `02_gamification.sql`, `README.md` (setup + seeding).
- `inference/` — the API: `main.py`, `agent.py`, `Dockerfile`, `README.md`.
- `scripts/` — `pull_sa_species.py`, `enrich_iucn.py`, `sa_species_list.csv`.
- `Lovable-Build-Prompt.md` + `lovable-prompts.md` — frontend build + follow-up prompts.
- `assets/critto-cover.svg` — cover image.
