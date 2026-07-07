# Critto — next session

The build is essentially done. The whole live app runs on AMD-hosted Fireworks (identify + entry),
and BioCLIP is validated on the AMD Instinct GPU. What's left is submission assets.

## Remaining, in order
1. **Test the live app** end to end in Lovable (upload real photos across birds/mammals/reptiles) and
   note any rough edges. Warm Render first (`/health`) to avoid the cold-start delay.
2. **README "AMD compute" section** — state it plainly for the auto pre-screen:
   "Identification and field-guide generation run live on AMD hardware via Fireworks AI (Minimax M3);
   the BioCLIP classifier is validated on AMD Instinct GPUs via ROCm."
3. **Slide deck (PDF)** — the pitch + AMD usage (pre-screened). Track 3 judging: creativity, originality,
   completeness, use of AMD platforms, product/market potential.
4. **Demo video** — app end-to-end + a few seconds of BioCLIP running on the AMD GPU (the 99.95% run).
   For live-ID shots you can just use the deployed app (it's real now).
5. Optional polish: cache the 150 entries in Supabase; reptile prompt tuning; more badge sets; multilingual names.

## Housekeeping
- Push tonight's code + docs: `git add . && git commit -m "Fireworks vision + docs" && git push`.
