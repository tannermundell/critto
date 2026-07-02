# GPU-Window Plan — front-load everything off-GPU

**Principle:** AMD GPU access is a short window (≈6–12 July — confirm exact dates with the
organisers). It's the scarcest resource. Spend it *only* on work that genuinely
needs the GPU. Everything else gets built and tested beforehand.

**The key trick:** build the whole app against a **mock inference API** that returns
correctly-shaped `/identify` and `/entry` responses. The frontend and Supabase flow
become fully working and demo-able before the GPU exists. When the window opens, swap
the mock for the real model server — same API contract — and integration is trivial.

---

## Key dates & credits (verify on the live page)

- **Register by 2 July** to get hackathon credits on day one. Later sign-ups: credits only from 7 July.
- **Hackathon credits (everyone):** $50 Fireworks AI. AMD Developer Cloud GPU access details shared at event start.
- **New-member credits (new AMD AI Developer Program sign-ups):** $100 AMD Developer Cloud + $50 Fireworks,
  via a separate **2–3 day manual approval that is NOT tied to the hackathon cutoff** — so signing up now
  may unlock Fireworks (and the $100 cloud credit) early.
- **GPU instances** are likely gated to event start regardless of when credits land, so the GPU window
  remains the only true GPU time. Fireworks (an API) is more likely usable as soon as credits arrive.
- **Action now:** (1) register for the hackathon before 2 July; (2) sign up to the AMD AI Developer Program
  as a new member to start the 2–3 day approval.
- Until Fireworks is live, build the agent against a **stand-in LLM behind a provider abstraction** — swapping
  to Fireworks is then a one-line config change.

---

## Build BEFORE the window (no GPU needed)

- **Species data** — done (`sa_species_list.csv`, 150 species).
- **Supabase** — run `schema.sql`, seed the species table, confirm auth + storage. (Schema is ready.)
- **Mock inference API** — small FastAPI app exposing `/identify` and `/entry`:
  - `/identify` returns 3 random species from the table with plausible confidence scores.
  - `/entry` returns a canned/structured field-guide entry.
  - Same request/response shape as the real server, so nothing downstream changes later.
- **Lovable frontend** — build all screens (capture/upload, candidate pick, result card,
  sightings log, auth), wired to Supabase and pointed at the mock API. Fully functional end-to-end.
- **Knowledge agent (`/entry`)** — build and test the full tool-use loop against **Fireworks AI**
  (or any hosted LLM as a stand-in if Fireworks access isn't live yet). The agent runs on Fireworks,
  not the GPU, so this needs no GPU window at all — it can be fully finished beforehand.
- **Vision inference code** — write the model-loading + inference code for `/identify` (BioCLIP).
  You can't *run* it on AMD hardware without the GPU, but it should be written, reviewed, and ready to deploy.
- **Containerization** — write the Dockerfile and get the server running in a container locally
  (against the mock/CPU). Public GitHub repo + README. This is a submission requirement; don't leave it to the end.
- **Fine-tune data prep** — if fine-tuning the vision model, download the training/eval images
  from iNaturalist now. Never burn GPU time downloading data.
- **Demo assets** — collect a set of known-good test photos (incl. tricky ones) for the eval set
  and the demo video.

## Build DURING the window (needs the GPU)

1. **Day 1, first thing — verify ROCm.** Load BioCLIP (the vision model) on the instance and confirm
   it runs. This is the single biggest risk; surface it immediately.
2. **Run real inference** and measure top-3 accuracy on the eval set.
3. **Fine-tune the vision model** only if zero-shot accuracy is weak.
4. **Swap the mock `/identify` for the real GPU model**; end-to-end integration test (the agent `/entry`
   on Fireworks is already done and unchanged).
5. **Benchmark + tune latency.**
6. **Record the final demo** against the real vision model.

Note: the agent LLM runs on Fireworks throughout, so the GPU window is spent *only* on the vision model.

---

## Suggested order before 6 July

1. Supabase live (schema + seed + auth). *(quick)*
2. Mock inference API running (locally or a free host). *(quick)*
3. Lovable frontend built against Supabase + mock — the demo essentially works. *(the big one)*
4. Agent tool-use loop working against a hosted LLM. *(parallelisable — your side)*
5. Inference server code written and reviewed, ready to deploy. *(your side)*
6. Fine-tune/eval images downloaded; demo test images chosen.

Result: when the GPU window opens, the only unknowns left are the genuinely GPU-bound ones —
which is exactly where the 6 days should go.
