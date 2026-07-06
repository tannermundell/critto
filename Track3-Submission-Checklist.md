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

## AMD support ruling — no live hosting needed
AMD support confirmed our project **does not need to be hosted live**; a recorded demo is acceptable.
So the persistent Developer Cloud VM is **off the critical path**. We evidence AMD-compute usage by:
- the vision model running on the **AMD Instinct GPU (ROCm)** — validated, Lion 99.95% (shown in the video),
- the LLM on **Fireworks AI** (AMD-hosted), which is also in the live Render pipeline once wired,
- **repo + slide deck** stating it explicitly (these are what the automated pre-screen reads — the video is not).

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
