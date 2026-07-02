# Animal ID App — Build Scope

**Name:** Critto
**One-liner:** Point your phone at a South African animal, get an instant ID plus a living field-guide entry — running on AMD GPUs.

---

## The product in one line

Upload or snap a photo of a bird, mammal, or reptile → the app identifies the species → an AI agent returns a grounded, well-designed field-guide entry.

---

## Core user flow (Phase 1)

1. User uploads an image or takes a photo.
2. App runs image recognition, returns the most likely species + confidence.
3. If confident: show the species card. If unsure: show top 3 candidates and let the user pick.
4. The knowledge agent assembles the field-guide entry for the confirmed species.
5. User sees a clean result card; optionally saves it to a personal sightings log.

---

## System architecture

Five layers. Keep them decoupled so Phase 2/3 bolt on without a rewrite.

**1. Frontend**
- Mobile-first web app. Camera capture + file upload.
- Result card is the hero screen — this is what wins the demo video. Species photo, common + scientific name, confidence, conservation-status badge, habitat, range, key facts.
- Empty/loading/error states designed properly (judges notice polish).

**2. Backend / API**
- Receives image, orchestrates the pipeline, returns structured results.
- Stateless where possible; one endpoint for "identify," one for "get species entry."

**3. Recognition layer (the AMD GPU hook)**
- Image classifier constrained to a curated **SA species list** (don't try to recognise all life — define the label set up front).
- **Fastest path:** use an existing open biological vision model (e.g. BioCLIP) in zero/few-shot mode against your SA species labels — minimal training, leans on a pre-trained model.
- **Stronger path:** fine-tune a vision model on SA observations (iNaturalist/GBIF data) for the chosen classes.
- Runs as PyTorch inference on **ROCm / AMD Developer Cloud** — this is your genuine "high-performance on AMD GPUs" story. Fine-tuning, if you do it, strengthens that story further.
- Always return **top-N candidates + confidence**, not a single guess — real photos are messy and this handles it gracefully.

**4. Knowledge agent layer (the "AI agent" hook)**
- Once a species is confirmed, an LLM agent builds the field-guide entry.
- **Grounded, not invented:** retrieve facts from curated sources (e.g. Wikipedia, IUCN Red List) and have the LLM *format* them — don't let it freestyle conservation status or range. This protects accuracy and business credibility.
- Output is structured: name, status, habitat, diet, size, range, "where you'd spot it," fun fact.

**5. Data**
- Species list + reference data: iNaturalist / GBIF for occurrences and images.
- Conservation status: IUCN Red List.
- Lock licensing early for any images you redistribute.

---

## Stack & architecture

**Track:** Track 3 (Unicorn) — product/startup project, judged on creativity, originality, completeness, use of AMD platforms, and product/market potential. No benchmarks.

**Guiding principle:** lean on AMD on two fronts — the **vision model runs on the AMD Developer Cloud GPU (ROCm)** and the **agent LLM runs on Fireworks AI (AMD-hosted models)**. Using both meaningfully maximises the "use of AMD platforms" judging criterion. All components are containerized (a submission requirement).

**Tooling by layer**

- **Frontend — Lovable.** Designed UI, native Supabase wiring, fast to iterate. Where the result card gets polished.
- **Backend / data — Supabase.** Auth, species database, image storage for uploads, sightings log. Talks to Lovable out of the box.
- **Inference + agent server — hand-written Python (FastAPI), built with Claude Code, containerized.** This is the part Lovable can't do. Exposes two endpoints: `/identify` (vision model, runs on the AMD GPU via ROCm) and `/entry` (knowledge agent, calls the LLM on Fireworks AI).

**Data flow**

```
┌──────────────┐      ┌──────────────────┐      ┌────────────────────────────┐
│   Lovable    │      │    Supabase      │      │  AMD Developer Cloud GPU   │
│  (frontend)  │      │ (backend / data) │      │ (FastAPI + PyTorch/ROCm)   │
│              │      │                  │      │                            │
│ upload/snap  │──1──▶│ storage + DB     │──2──▶│ /identify (vision model)   │
│ result card  │◀─────│ edge functions   │◀─3───│   → top-N + confidence     │
│ confirm pick │──4──▶│                  │      │                            │
│              │      │                  │──5──▶│ /entry (knowledge agent)   │
│              │◀─────│ save sighting    │◀─6───│   → grounded field guide   │
└──────────────┘      └──────────────────┘      └────────────────────────────┘
```

1. User uploads or snaps a photo → Supabase Storage.
2. Supabase edge function calls the GPU server's `/identify`.
3. AMD GPU runs the vision model → returns top-N species + confidence.
4. User confirms the species (or picks from the top 3).
5. Edge function calls `/entry`; the knowledge agent runs its tool-use loop.
6. AMD GPU returns the grounded field-guide entry → Supabase saves it → Lovable renders the card.

**Make the agent genuinely agentic.** `/entry` should not be a single LLM prompt. It takes the species → calls retrieval tools (Wikipedia, IUCN) → synthesises grounded, structured fields via the Fireworks-hosted LLM. A lightweight tool-calling loop (LangChain/LlamaIndex or hand-rolled) is enough — the point is multi-step reasoning with tools.

**LLM hosting — decided:** the agent LLM runs on **Fireworks AI** ($50 credits, models hosted on AMD hardware). It satisfies "use of AMD platforms" without the effort of self-hosting on ROCm, and means the scarce GPU window is needed only for the vision model.

**Watch-outs**

- **GPU credits.** $100 of GPU time burns while the instance runs. Have it up for dev sessions and the demo; shut it down otherwise.
- **Fireworks credits.** $50 cap — cache agent entries per species so you don't re-generate.
- **Expose the endpoint early.** Supabase needs to reach the inference server — sort out a public URL + auth token up front, not on the last day.
- **Containerize from the start.** Submission requires a Docker container, a public GitHub repo with a README, and a runnable app. Build it in; don't bolt it on at the end.

---

## Phase 1 — what's IN

- Image upload + camera capture
- Recognition across **birds, mammals, reptiles** within a defined SA species set
- Confidence scoring + top-3 candidate fallback
- Grounded species field-guide entries via the knowledge agent
- Designed result card (the showpiece)
- Personal sightings log / collection (optional but cheap, and birders love a "life list" — adds stickiness and demo appeal)

## Phase 1 — what's explicitly OUT

- Sound recognition (Phase 2)
- Any species outside South Africa (Phase 3)
- Real-time video detection — still images only
- Offline mode
- Heavy user accounts — keep auth minimal or skip for the demo

---

## Technical decisions to lock early

- **Define the SA species list first.** Coverage scope drives everything. Start with a manageable set (e.g. common/iconic species per class) rather than exhaustive.
- **Verify ROCm compatibility** of your chosen model before committing — some models need porting to run cleanly on AMD GPUs. Test this on Day 1, not Day 10.
- **Decide zero-shot vs fine-tune** based on how the model performs on your SA set out of the box.
- **Reptile coverage is the weak link** — they're under-represented in many datasets and harder to tell apart. Set expectations, lean on top-N, and consider a smaller reptile set than birds/mammals.

---

## Where it scores (Track 3 judging criteria)

- **Creativity & originality:** localised SA focus + a grounded field-guide agent, not a generic image classifier.
- **Product/market potential:** SA tourism, safari operators, birding, conservation/education — a real market.
- **Completeness:** a polished, working end-to-end demo (the result card is your design edge here).
- **Use of AMD platforms:** AMD on two fronts — vision inference on the AMD GPU (ROCm) + the agent LLM on Fireworks AI.

---

## Phase 2 — Sound (features added, no build plan)

- **Audio capture:** record or upload an animal call in-app.
- **Bioacoustic recognition:** integrate a sound-ID model (e.g. BirdNET for birds) as a parallel input alongside image — same "identify → confirm → field-guide entry" flow.
- **Multi-modal confirmation:** if a user has both a photo and a call, cross-check the two for a higher-confidence ID.
- **Expanded entry:** add a playable reference call to each species card so users can compare.
- **Use case unlock:** identifying animals you can hear but can't see — a big deal for birding.

## Phase 3 — Beyond SA (features added, no build plan)

- **Region selector:** user picks their region/country; the app loads the relevant species set.
- **Expanded model coverage:** broaden recognition to additional regional species sets, region by region.
- **Localised entries:** range maps, conservation status, and "where to spot it" adapt to the selected region.
- **Travel/tourism angle:** "what wildlife will I see in [destination]" — positions the app for international travellers, not just locals.
- **Community data:** optionally let user sightings feed back in to improve coverage and build a contribution loop.
