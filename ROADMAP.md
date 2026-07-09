# Critto — Feature Roadmap (brother's ideas, triaged)

## Already in Phase 1
- **Index of what you've spotted** — this is the sightings log / "life list" already built
  (Supabase `sightings` table + the Lovable app). Levels and points can build straight on top of it.

## Phase 1 candidates — cheap, high demo value, mostly free from data we already have

> **Status:** rarity cards, read-aloud voice, and the introduced/alien flag are **built**.
> Collection sets & badges and levels/points are still to do.
- **Collectible cards + rarity tiers.** Reframe the sightings log as a *collection* of cards, and derive
  a rarity tier (Common → Uncommon → Rare → Very Rare → Legendary) from `sa_observations`, which we
  already pulled for all 150 species. Rarity is essentially free data-wise; the payoff is big for the
  Track 3 "creativity" and "product/market potential" scores. UI effort: medium.
- **Introduced / "alien" flag.** A simple global boolean on species marking non-natives (e.g. Eastern
  Gray Squirrel, House Sparrow). Only a handful of our 150 need flagging — quick to curate. Adds
  credibility and a conservation angle. Low effort. (The *location-specific* version is future — see below.)
- **Read-aloud voice.** A "Listen" button on the entry using the browser's built-in Web Speech API
  (SpeechSynthesis). No backend, no cost, works today. Accessibility + a nice wow moment. Low effort.
- **Simple levels / points.** Derived from the count and rarity of a user's sightings. Low effort once
  rarity exists.
- **Collection sets & badges.** Reward completing a themed *set* of sightings with a **badge / coin /
  medallion** — deliberately a different reward type from the animal cards, so it reads as an achievement/
  trophy rather than just another card. Two-tier system: cards = animals collected, badges = sets
  completed. Mechanically simple: a set is just a species list (or a filter), and the badge unlocks when a
  user's sightings cover it. Sets buildable from data we already have:
  - **Big Five** — Lion, Leopard, African Savanna Elephant, African Buffalo, White Rhino (all in our 150).
  - **Endangered Guardians** — all threatened species, filtered by `iucn_status` (free, and reinforces the
    conservation message).
  - **Class masters** — Birder / Herper / Mammal Tracker for completing a share of each class.
  - Thematic sets (Antelope Collector, Predators, etc.).
  - **Tiered coins** — bronze/silver/gold by count within a class (e.g. Mammals 10 = bronze, 25 = silver,
    50 = gold; likewise Birds and Reptiles). Turns each class into a progression, not a single unlock.
  - Brainstorm more sets next session (e.g. a "Baby Five"-style set).
  - *Not yet:* **Little Five** (only the leopard tortoise is in our list) and **location/biome sets**
    (need per-location data — pair with Phase 3).

## Future (Phase 2 / 3+)
- **Sighting verification / anti-cheat.** Checking a photo was really taken in the field (EXIF, geotag,
  timestamp, image authenticity). Needs proper anti-abuse design — future.
- **Social & games.** Vs-friends, seasonal/temporary challenges, leaderboards. Needs a social layer and
  backend — future.
- **Location-specific alien marking.** Dynamically flag a species as introduced *for the searched
  location*. Needs per-region range data — pairs naturally with the Phase 3 "beyond SA" expansion.
- **"Heard-only" cards.** Greyed card with a headphone badge when a species is identified by sound.
  Depends on the Phase 2 sound feature.
- **Conversational AI voice assistant.** Beyond simple read-aloud — a back-and-forth voice guide. Future.

## Recommendation
Nail the core first: accurate ID + a polished result card. If there's time before the deadline, add in
this order for best return and judging impact:
1. **Rarity cards** (biggest pitch payoff, data already exists)
2. **Read-aloud** (near-zero effort, nice completeness point)
3. **Alien flag** (credibility + conservation, quick curate)

All three are cheap and push directly on the Track 3 criteria (creativity, completeness, product/market
potential). Everything in the Future bucket is genuinely good — just not worth pulling into a time-boxed
hackathon build.
