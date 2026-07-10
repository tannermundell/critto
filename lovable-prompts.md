# Critto — Lovable prompts (log)

The **initial build prompt** lives in `Lovable-Build-Prompt.md`. This file logs the follow-up
prompts used to extend the app. All below are marked ✓ applied.

---

## 1. Initial build ✓
See `Lovable-Build-Prompt.md` — auth, Identify flow (upload → candidates → confirm), result card,
Journal, wired to your own Supabase + the Render API. Built UI-first with no Lovable Cloud.

## 2. About section ✓
> On the result card, add an "About" section that displays the `summary` field returned by `/entry` — a short paragraph shown under the species name and status badge, above Habitat/Diet/etc. If `summary` is empty, hide the section. Leave everything else unchanged.

## 3. Collection + rarity ✓
> The `species` table now has a `rarity` field (Common, Uncommon, Rare, Very Rare, Legendary). Add a Collection screen: a grid of all species as cards, each styled by its rarity (distinct colour/border treatment, Legendary the most striking). Species the user has a sighting of show as "collected" — full colour with the species photo; species not yet spotted show locked/greyed silhouettes. Show a progress count (e.g. "23 / 150 collected"). Tapping a collected card opens its existing entry view. Add Collection to the bottom navigation.

## 4. Introduced / alien badge ✓
> The `species` table has an `introduced` boolean. On both the result card and the collection card, if `introduced` is true, show a small "Introduced" badge (distinct colour, e.g. orange) marking it as a non-native species.

## 5. Read-aloud voice ✓
> On the result/entry card, add a "Listen" button that uses the browser Web Speech API (`window.speechSynthesis`) to read the entry aloud — common name, IUCN status, the About summary, then the field-guide fields. Toggle between play and stop, and stop any ongoing speech when the user leaves the screen.

## 6. Named locked cards ✓
> On the Collection screen, locked (not-yet-spotted) cards should still show the species common name and its rarity badge, with a greyed silhouette/lock in place of the photo. Keep the real photo as the reward shown only once collected. Remove the "???" placeholder — always show the actual name.

## 7. Hide "Not documented" fields ✓
> On the result card, hide any field whose value is "Not documented" — including the Fun Fact highlight. If all the field-guide fields are missing, show just the About summary. Never display the literal text "Not documented".

## 8. Rename My List → Journal ✓
> Rename the "My List" tab/screen to "Journal".

---

## 9. Desktop responsiveness
> Make Critto responsive for desktop, not just mobile/tablet. It currently renders as a narrow centred column on wide screens. On larger viewports: use a wider max content width; lay the Collection and Journal out as multi-column grids (roughly 4–5 cards per row on desktop, 2–3 on tablet, 1–2 on mobile); where it improves readability, give the result/entry card a two-column layout on wide screens (species image beside the details); and make the navigation and spacing feel intentional on desktop. Keep the mobile experience unchanged.

## 10. Badges / sets view
> Add a Badges feature. A badge is earned when a user's collected species satisfy a set — compute earned/locked on the fly from the user's sightings (no new tables needed). Add a Badges section (on the Collection screen, above the species grid, or as its own tab) showing each badge as a coin/medallion: earned badges in full colour, locked ones greyed with progress (e.g. "3/5"). Make badges visually distinct from the animal cards — they're achievements, not collected animals. Sets:
> - **Big Five** — spot all of: Lion (Panthera leo), Leopard (Panthera pardus), African Savanna Elephant (Loxodonta africana), African Buffalo (Syncerus caffer), White Rhinoceros (Ceratotherium simum).
> - **Endangered Guardian** — spot any 5 species whose `iucn_status` is Vulnerable, Endangered, or Critically Endangered.
> - **Birder** — spot 10 species of class Aves.
> - **Mammal Tracker** — spot 10 species of class Mammalia.
> - **Herper** — spot 10 species of class Reptilia.

## 11. Home page copy
> On the home page, change the text "Add it to your personal life list." to "Add it to your journal."

## 12. Collection uses stock images (not user photos)
> On the Collection screen, each species card should use the species' reference image from the `species.photo_url` field (the stock photo) — NOT the user's uploaded sighting photo. Collected species show that reference photo in full colour; not-yet-spotted species show it locked/greyed (or a silhouette) with the name and rarity. Keep the user's own uploaded photos in the Journal, not the Collection.

## 13. Robustly hide "Not documented" fields
> On the result card, hide any field-guide field whose value — after trimming whitespace and any trailing punctuation, and ignoring case — equals "not documented" (also hide empty values). Apply this to every field including the Fun Fact box and "Where to spot it." If all field-guide fields end up hidden, show just the About summary. Never render the literal text "Not documented" to the user.

## Not yet prompted (future)
- Badge/coin rewards for completing sets (Big Five, Endangered Guardians, class masters).
- Levels / points from sightings count + rarity.
- Region picker + location-specific alien marking (Phase 3 data-dependent).
