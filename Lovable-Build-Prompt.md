# Lovable Build Prompt — Critto

> This is the **initial** build prompt. Follow-up prompts (About section, Collection + rarity,
> read-aloud, introduced badge, named locked cards, hide "Not documented", My List → **Journal**)
> are logged in `lovable-prompts.md`. Note: the "My Sightings / My List" screen below is now called **Journal**.

Paste everything in the box below into Lovable as your initial build prompt. Before you do:

1. Build first with the prompt below, THEN connect your own Supabase project (Lovable can't connect it until an app exists). The prompt tells Lovable not to use Lovable Cloud.
2. The mock API URL is already wired into the prompt below (`https://critto-mock.onrender.com`).
3. The Supabase tables (`species`, `sightings`) and the `sightings` storage bucket already exist
   from `db/schema.sql` — the prompt tells Lovable to use them, not recreate them.

---

## THE PROMPT

Build a mobile-first web app called **Critto**. Tagline: "Identify South Africa's wildlife from a photo."

Critto lets a user photograph a South African animal (bird, mammal, or reptile), identifies the
species, and shows a rich field-guide entry. Users can save their identifications to a personal
"life list."

**IMPORTANT — backend:** Do NOT use or enable Lovable Cloud, and do NOT provision any built-in
database or auth. I will connect my own existing **Supabase** project immediately after this first
build. Build the UI now and wire all auth, database, and storage through Supabase (supabase-js); it
will start working once I connect my project. Use environment variables/placeholders for the Supabase
URL and anon key that get filled when I connect.

### Tech & integrations
- All auth, database, and storage go through **my Supabase** project (connected after this build) — not
  Lovable Cloud. Do NOT create or migrate tables: my Supabase already has the `species` and `sightings`
  tables and a private `sightings` storage bucket (described below). Use them as-is once connected.
- Call an external **inference API** for identification and field-guide content. Store its base URL as a
  single config constant: `API_BASE_URL = "https://critto-mock.onrender.com"`. All calls go to `{API_BASE_URL}/identify`
  and `{API_BASE_URL}/entry`.
- Require login (Supabase email/password auth). Row Level Security already restricts each user to their
  own sightings.

### Existing data model (do not recreate)
- `species`: id, class ('Aves'|'Mammalia'|'Reptilia'), common_name, scientific_name, iucn_status,
  inat_taxon_id, sa_observations, photo_url.
- `sightings`: id, user_id, species_id, image_url, confidence, candidates (jsonb), latitude, longitude,
  created_at.
- Storage bucket `sightings` (private): upload user photos under a folder named with their user id,
  e.g. `{user_id}/{filename}`.

### API contract
`POST {API_BASE_URL}/identify`
- Request: `{ "image_url": "<signed url to the uploaded photo>" }`
- Response: `{ "candidates": [ { "common_name", "scientific_name", "class", "confidence", "photo_url" } ], "model_version" }`
  (up to 3 candidates, confidence is 0–1, highest first)

`POST {API_BASE_URL}/entry`
- Request: `{ "species": { "common_name", "scientific_name", "class" } }`
- Response: `{ "common_name", "scientific_name", "iucn_status", "habitat", "diet", "size", "range", "where_to_spot", "fun_fact", "sources": [], "model_version" }`

### Screens & flow
1. **Auth** — clean sign-up / log-in (email + password). Critto logo and tagline.
2. **Capture (home)** — primary screen. A big "Identify an animal" action that lets the user either
   take a photo (device camera) or upload an image. Show a friendly empty state explaining what Critto does.
3. **Identifying (loading)** — after the photo is chosen:
   - Upload the image to the `sightings` bucket under the user's folder.
   - Create a signed URL for it and POST it to `/identify`.
   - Show a pleasant loading state while waiting.
4. **Candidate selection** — show the returned candidates:
   - If the top candidate's confidence ≥ 0.70, present it prominently as "We think this is a …" with its
     photo and confidence, plus a smaller "Not right? See other matches" revealing the other candidates.
   - If below 0.70, present all candidates as a choosable list ("Which one looks right?").
   - Each candidate shows common name, scientific name (italic), class, confidence, and thumbnail (photo_url).
   - User taps to confirm the correct species.
5. **Result card (the hero screen — make this beautiful)** — on confirmation, POST the chosen species to
   `/entry` and render a field-guide card:
   - Species photo (use the candidate's photo_url), common name (large), scientific name (italic, muted).
   - A coloured **IUCN status badge** (see colour mapping below).
   - Sections: Habitat, Diet, Size, Range, "Where to spot it," and a highlighted "Fun fact."
   - A **Save to my sightings** button.
6. **Save** — write a row to `sightings`: user_id, species_id (look up by scientific_name in `species`),
   image_url (the stored path), confidence (top candidate), candidates (the full /identify response).
   Capture latitude/longitude if the user permits geolocation; otherwise leave null.
7. **My Sightings (life list)** — a grid/list of the user's saved sightings (photo, common name, date,
   status badge), newest first. Tapping one reopens its result card. Friendly empty state for new users.

Use a bottom navigation bar: **Capture** and **My Sightings** (plus a small profile/sign-out menu).

### IUCN status badge colours
- Least Concern → green
- Near Threatened → yellow-green
- Vulnerable → amber
- Endangered → orange
- Critically Endangered → red
- Not Evaluated / blank → grey

### Design direction
- Mobile-first, clean, modern, with a South African nature feel. Generous whitespace, rounded cards,
  smooth transitions.
- Palette: deep teal/green (#0b2e2b, #175049), warm amber/sand (#d9842c, #f6c451), cream (#fdf7ea),
  soft mint accent (#9fd6c6). Dark text on light backgrounds; the result card can use a warm header.
- The result card is the centrepiece — make it feel polished and shareable.
- Include proper empty, loading, and error states everywhere (e.g. if the API is unreachable, show a
  friendly retry message).

### Out of scope (do not build)
- Sound/audio identification.
- Species outside South Africa.
- Real-time video detection (still images only).
