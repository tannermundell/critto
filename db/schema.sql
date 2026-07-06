-- =====================================================================
-- Critto — Supabase / Postgres schema (Phase 1)
-- Run this in the Supabase SQL Editor (Database > SQL Editor > New query).
-- Order matters: run top to bottom once on a fresh project.
-- =====================================================================

-- gen_random_uuid() — enabled by default on Supabase, included here for safety.
create extension if not exists "pgcrypto";


-- ---------------------------------------------------------------------
-- SPECIES  (reference data — seeded from scripts/sa_species_list.csv)
-- Read-only to app clients; written only via the backend service role.
-- Columns are aligned to the CSV headers so you can use Supabase's
-- built-in CSV import directly (see db/README.md).
-- ---------------------------------------------------------------------
create table if not exists public.species (
    id               uuid primary key default gen_random_uuid(),
    class            text not null check (class in ('Aves', 'Mammalia', 'Reptilia')),
    common_name      text not null,
    scientific_name  text not null unique,
    iucn_status      text,
    inat_taxon_id    bigint,
    sa_observations  integer,
    photo_url        text,
    -- gamification (populated by db/02_gamification.sql):
    rarity           text,
    introduced       boolean not null default false,
    -- filled at runtime by the knowledge agent (grounded field-guide entry):
    cached_entry     jsonb,
    -- optional: label the vision model emits, if it differs from scientific_name:
    model_label      text,
    created_at       timestamptz not null default now()
);

create index if not exists species_class_idx       on public.species (class);
create index if not exists species_common_name_idx on public.species (common_name);


-- ---------------------------------------------------------------------
-- SIGHTINGS  (per-user "life list")
-- Each row is one confirmed (or pending) identification by a user.
-- location kept as plain lat/lng to avoid a PostGIS dependency in Phase 1.
-- ---------------------------------------------------------------------
create table if not exists public.sightings (
    id           uuid primary key default gen_random_uuid(),
    user_id      uuid not null references auth.users (id) on delete cascade,
    species_id   uuid references public.species (id),   -- null until confirmed
    image_url    text not null,                         -- path in the 'sightings' bucket
    confidence   real,                                  -- top candidate score (0–1)
    candidates   jsonb,                                 -- full top-N from /identify
    latitude     double precision,                      -- optional
    longitude    double precision,                      -- optional
    created_at   timestamptz not null default now()
);

create index if not exists sightings_user_idx    on public.sightings (user_id);
create index if not exists sightings_species_idx on public.sightings (species_id);


-- =====================================================================
-- ROW LEVEL SECURITY
-- =====================================================================

-- SPECIES: anyone (incl. anonymous) may read; no client writes.
-- The backend updates cached_entry using the service-role key, which
-- bypasses RLS, so no write policy is needed here.
alter table public.species enable row level security;

drop policy if exists "species readable by everyone" on public.species;
create policy "species readable by everyone"
    on public.species for select
    using (true);


-- SIGHTINGS: each user can only see and manage their own rows.
alter table public.sightings enable row level security;

drop policy if exists "read own sightings"   on public.sightings;
drop policy if exists "insert own sightings" on public.sightings;
drop policy if exists "update own sightings" on public.sightings;
drop policy if exists "delete own sightings" on public.sightings;

create policy "read own sightings"
    on public.sightings for select
    using (auth.uid() = user_id);

create policy "insert own sightings"
    on public.sightings for insert
    with check (auth.uid() = user_id);

create policy "update own sightings"
    on public.sightings for update
    using (auth.uid() = user_id);

create policy "delete own sightings"
    on public.sightings for delete
    using (auth.uid() = user_id);


-- =====================================================================
-- STORAGE  (uploaded sighting photos)
-- Private bucket; images stored under a per-user folder: <user_id>/<file>.
-- Species reference images use external iNaturalist URLs, so they need
-- no storage here.
-- =====================================================================
insert into storage.buckets (id, name, public)
values ('sightings', 'sightings', false)
on conflict (id) do nothing;

drop policy if exists "upload own sighting images" on storage.objects;
drop policy if exists "read own sighting images"   on storage.objects;

create policy "upload own sighting images"
    on storage.objects for insert to authenticated
    with check (
        bucket_id = 'sightings'
        and (storage.foldername(name))[1] = auth.uid()::text
    );

create policy "read own sighting images"
    on storage.objects for select to authenticated
    using (
        bucket_id = 'sightings'
        and (storage.foldername(name))[1] = auth.uid()::text
    );
