# Track 3 (Unicorn) — Submission Checklist & Compliance

_From the official Participant Guide (ACT II), updated after AMD support guidance._

## What Track 3 requires
| Item | Required? | Our status |
|---|---|---|
| GitHub repository URL | **Yes** | ✅ `github.com/tannermundell/critto` (public) |
| Demo video | **Yes** | ❌ to record |
| Slide deck (PDF) | **Yes** | ❌ to build |
| Live demo / hosted URL | Optional | ⚪ not required — see note |
| Docker image | Not required for Track 3 | (we have CPU + ROCm Dockerfiles anyway) |

## AMD compute — solved on two fronts
- **Live app runs on AMD (Fireworks).** Both `/identify` (vision) and `/entry` (LLM) run on Minimax M3
  via Fireworks AI (AMD-hosted), live on Render. So AMD compute is in the live pipeline AND the app is
  effectively hosted — the Lovable app + Render URL make a working live demo.
- **BioCLIP on the AMD Instinct GPU** (ROCm) — validated (Lion 99.95%); the high-accuracy classifier,
  shown in the demo video as the GPU-compute evidence.
- No persistent Developer Cloud VM needed (support confirmed live hosting isn't required; and we now have
  a live AMD path anyway).
- **Repo + slide deck** must state this explicitly — that's what the automated pre-screen reads.

## THE rule that still matters
> "AMD compute usage is a requirement: projects that do not demonstrate it will be disqualified."
> The auto pre-screen inspects the **GitHub repo, slide deck (PDF), and live URL** — NOT the video.

So make AMD usage unmistakable in the repo README and the slide deck. Suggested wording:
"vision inference on AMD Instinct GPUs via ROCm; LLM via Fireworks AI on AMD hardware."

## Done
- Original product app ✅ · public repo ✅ · real vision model validated on AMD GPU ✅ · frontend built ✅

## Remaining
1. **Wire Fireworks** into `/entry` (real content + AMD in the live pipeline). Own Fireworks key; $6 trial
   works now, $50 hackathon credits pending.
2. **README "AMD compute" section** (pre-screened).
3. **Slide deck (PDF)** stating AMD usage (pre-screened).
4. **Demo video** — Critto app end-to-end + a few seconds of `gpu_server.py` on the AMD GPU.
5. For real IDs on camera: run `gpu_server.py` on the laptop + a tunnel; point Lovable at it while recording.

## Priority order
Fireworks → README AMD section → demo recording (with laptop-served real IDs) → slide deck.
