# Track 3 (Unicorn) — Submission Checklist & Compliance

_From the official Participant Guide (ACT II)._

## What Track 3 requires
| Item | Required? | Our status |
|---|---|---|
| GitHub repository URL | **Yes** | ✅ `github.com/tannermundell/critto` (public) — but must clearly show AMD usage |
| Demo video | **Yes** | ❌ not made yet |
| Slide deck (PDF) | **Yes** | ❌ not made yet |
| Live demo / hosted URL | Optional (recommended) | ✅ Lovable app — include it |
| Docker image | **Not required** for Track 3 | (we have one anyway — useful for AMD Cloud) |

## THE critical rule
> **"AMD compute usage is a requirement: projects that do not demonstrate it will be disqualified."**
> And: **automated pre-screening only inspects the GitHub repo, the slide deck (PDF), and the live/hosted URL — it does NOT process the demo video.**

So AMD compute must be **visible in the repo + slide deck + live URL**, not just shown in the video.
This reframes our priorities:

- **Fireworks isn't just "fill the entry fields" — it's part of meeting the AMD requirement.** Fireworks
  models run on AMD hardware, so routing `/entry` through Fireworks puts AMD compute in the live pipeline.
- **Run the vision model on AMD Developer Cloud GPU** (access: https://notebooks.amd.com/hackathon).
  This is the headline AMD compute and also replaces the mock `/identify` with a real model.
- **Document AMD usage explicitly** in the README and the slide deck (the prescreen reads these). Use clear
  language: "vision inference on AMD Instinct GPUs via ROCm; LLM via Fireworks AI on AMD hardware."

## How we align (and gaps)
Doing right:
- Original, product-oriented AI app ✅
- Public GitHub repo ✅
- Live hosted demo (Lovable) ✅
- Architecture already designed around AMD (GPU vision + Fireworks LLM) ✅

Gaps to close:
1. **Wire Fireworks** into `/entry` (AMD compute in the live path + real entries). Uses your $50 hackathon
   Fireworks credits + your own Fireworks API key (the harness-injected key is only for Tracks 1 & 2).
2. **Run the vision model on AMD Developer Cloud GPU** during the window; swap the mock `/identify` for it.
3. **README: add an explicit "AMD compute" section** so the prescreen sees it.
4. **Build the slide deck (PDF)** — state AMD usage clearly (prescreened).
5. **Record the demo video** (human judges only).
6. **Keep the live URL warm** during judging — Render free tier sleeps (~50s cold start), which could look
   broken. Warm it, or move the inference service onto the AMD Cloud / a paid tier for the judging window.

## General rules that apply to our live demo
- Responses under **30 seconds** per request — fine, but mind Render cold starts.
- All responses in **English** ✅
- No hardcoded/cached answers — our real vision model must genuinely identify (retire the random mock).

## Priority order
1. Fireworks wired (AMD in the live pipeline now).
2. GPU window: real vision model on AMD Cloud → swap mock `/identify`.
3. README AMD section + slide deck (both prescreened).
4. Demo video.
5. Warm/host the live URL for judging.
