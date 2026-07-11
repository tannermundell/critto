# Critto — Demo Video Shot List & Script

**Target length:** ~2 minutes (check lablab's max and stay under it).
**Goal:** show a real, working product + make the AMD usage unmistakable (human judges watch this; it isn't
auto-screened, so it's your chance to be compelling). Judging: creativity, originality, completeness, use
of AMD platforms, product/market potential.

**Record:** app on a phone screen-recording if you can (feels natural for "snap a photo"); desktop browser
at 1080p is fine too. Plus one screen-grab of the AMD notebook output.

---

## The flow (scene by scene)

| Time | On screen | Voiceover | Notes |
|---|---|---|---|
| 0:00–0:10 | Critto title/logo over a striking SA wildlife shot, then the app's capture screen | "This is a lion. This is a boomslang. This is a Cape sugarbird. Most people in South Africa couldn't name them — Critto can." | Hook fast. Show 2–3 quick animal photos. |
| 0:10–0:22 | The result card scrolling — habitat, diet, conservation status | "But knowing a name isn't knowing the animal — you forget it, and there's nothing to keep you exploring. Critto goes deeper." | Positive framing; show the depth, don't knock others. |
| 0:22–1:00 | **Live demo (the star).** Open critto.org → take/upload an animal photo → identifying → top-3 with confidence → tap the right one → the result card | "Snap a photo. Critto identifies the species and writes a full field guide — habitat, diet, where to spot it, conservation status — grounded in real sources, read aloud if you like." | Warm the API first (hit /health) so there's no cold-start wait. Show the card scrolling: About, IUCN badge, Listen button. |
| 1:00–1:12 | A second quick ID — a reptile or bird | "Birds, mammals, reptiles — 150 South African species and growing." | Shows breadth; keeps momentum. |
| 1:12–1:32 | **Collection + coins + Journal.** Scroll the collection grid (locked/greyed vs collected, rarity), a coin (Big Five), the Journal | "Every sighting earns a card. Rarer, more threatened species are worth more. Complete sets like the Big Five to earn coins. It turns getting outside into a game — with a conservation heart." | This is the product/market + originality beat. |
| 1:32–1:52 | **The AMD moment.** Cut to the notebook: `/health` showing `device: cuda`, `hip: 7.2`, then the BioCLIP result `Lion 99.95%` | "Under the hood: our vision model runs on an AMD GPU via ROCm — 99.95% on our test. And the live app's inference runs through Fireworks AI, AMD's inference partner. AMD on two fronts." | The credibility shot. Screen-record the actual cell output. Add a text caption: "AMD GPU (ROCm) + Fireworks AI". |
| 1:52–2:00 | Close: Critto logo + "critto.org" + QR + "Aidan Dean · Tanner Mundell" | "Critto. Reconnecting people with the wild — one photo at a time. Try it at critto.org." | End card = your slide 11/12 look. |

---

## Voiceover script (clean read)

> This is a lion. This is a boomslang. This is a Cape sugarbird. Most people in South Africa couldn't
> name them — Critto can.
>
> But knowing a name isn't knowing the animal. You forget it, and there's nothing to keep you exploring.
> Critto goes deeper — built to help you learn about the wildlife around you.
>
> Snap a photo, and Critto identifies the species and writes a full field guide — habitat, diet, where to
> spot it, conservation status — grounded in real sources, and read aloud if you like. Birds, mammals,
> reptiles: 150 South African species and growing.
>
> Every sighting earns a card. Rarer and more threatened species are worth more. Complete sets like the
> Big Five to earn coins. It turns getting outside into a game — with a conservation heart.
>
> Under the hood, our vision model runs on an AMD GPU via ROCm — 99.95% on our test. And the live
> app's inference runs through Fireworks AI, AMD's inference partner. AMD on two fronts.
>
> Critto. Reconnecting people with the wild — one photo at a time. Try it at critto.org.

---

## Production checklist

- **Warm the API** (`/health` on the Render URL) right before recording so identification is instant, not a cold start.
- **Have good sample photos ready** — your own snaps of real animals are ideal; otherwise clean photos to upload. Test them beforehand so the IDs land well on camera.
- **Confirm critto.org is live** (DNS pointed at the app) before filming the URL/QR.
- **Clean recording:** full-screen browser, no stray tabs/notifications; 1080p; landscape.
- **Text overlays** for the key claims — especially the AMD line (AMD GPU + Fireworks) — since judges skim.
- **Keep it tight:** if a section runs long, cut narration before cutting the demo. The working app is the point.
- **Music:** subtle, low; don't drown the voiceover. Export with captions if the platform allows.
