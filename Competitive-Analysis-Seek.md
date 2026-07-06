# Critto vs Seek — Competitive Analysis

_Research date: July 2026._

## What Seek is
Seek by iNaturalist — a global species-ID app.
- Identifies **~80,000 species** (plants, animals, fungi) worldwide.
- **Real-time, on-device camera recognition that works fully offline** (no internet needed).
  Guides you down the tree of life as you frame the subject.
- **No account / no registration**, no data collected, location obscured — privacy-first, popular
  with families, kids, and schools.
- Gamification: badges for observations + seasonal challenges.

## Seek's documented weaknesses
- Variable accuracy on some groups (e.g. trees), limited improvement over time.
- **No cloud backup/sync** — switching phones loses observations, badges, achievements (a top complaint).
- No credit when a photo Seek couldn't ID is later identified on iNaturalist.
- Gamification criticised as **shallow** — users earn badges but don't actually learn to name species.
- Occasional crashes.

## Where Critto already differs / wins
| Dimension | Seek | Critto |
|---|---|---|
| Focus | Global generalist, 80k species, plants+animals+fungi | South African specialist, curated animals (birds/mammals/reptiles) |
| Content | Name + brief facts | AI-written, **cited** field-guide entry (Wikipedia + IUCN) + read-aloud |
| Persistence | No account, **no backup** (data loss on device change) | Cloud account (Supabase) — sightings, collection, badges synced |
| Gamification | Generic badges/challenges | Conservation-weighted rarity, collection dex, themed sets (Big Five, Endangered Guardians) |
| Conservation | Not emphasised | IUCN status foregrounded; rarity floored by threat level |
| Market | Generic hobbyist | SA tourism / safari / birding / education |

## Where Seek beats us today (gaps)
- **Offline, real-time, on-device identification** — critical in reserves with poor signal, which is
  exactly Critto's market. Critto is currently cloud-only (upload → API). **Most important gap.**
- **Zero-friction start** — no login; instant use. Critto's account gate adds friction (but enables sync).
- **Coverage & battle-tested accuracy** — 80k species vs our 150.

## Recommendations (prioritised)
1. **Own local depth (moat).** Multilingual common names (Afrikaans, isiZulu, isiXhosa), park/region
   context, and "what you'll see at Kruger/Kgalagadi" trip lists. Seek has none of this.
2. **Make conservation the identity.** Highlight threatened species, "spotted an endangered animal"
   moments, links to SA conservation orgs. Purpose Seek lacks.
3. **Fix the learning gap Seek is criticised for.** A light "learn mode" — quizzes on species you've
   seen, "how to tell X from Y" ID tips. Turns collecting into real retention.
4. **Market the cloud sync** explicitly — "never lose your life list."
5. **Roadmap: offline / on-device fallback model** for no-signal reserves — neutralises Seek's core
   strength in our own market. Strategic, not hackathon-scope.
6. **Sound ID (Phase 2)** for further differentiation — but note **Merlin** (Cornell) owns birds-by-sound,
   so lean on multi-taxa + local angle rather than competing head-on.

## Other competitors to keep in view
- **Merlin Bird ID** (Cornell) — excellent bird ID incl. sound; the one to respect if we add audio.
- **Google Lens / PlantNet / Picture Insect** — generalist or niche ID tools; none are SA-localised or
  conservation-framed.

## Sources
- https://www.inaturalist.org/pages/seek_app
- https://www.inaturalist.org/blog/23075-real-time-computer-vision-predictions-in-seek-by-inaturalist-version-2-0
- https://apps.apple.com/us/app/seek-by-inaturalist/id1353224144
- https://www.safes.so/blogs/seek-by-inaturalist/
- https://medium.com/@clairedlmk/when-gamification-goes-wrong-b19cca8842bd
- https://forum.inaturalist.org/t/seek-app-vs-inaturalist/16606
