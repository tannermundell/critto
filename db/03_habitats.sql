-- =====================================================================
-- Critto — habitat/area tags (for the Explore area filter + richer info)
-- Run once in the Supabase SQL Editor, then run scripts/enrich_habitats.py
-- to populate. Safe to re-run.
-- =====================================================================

alter table public.species add column if not exists habitats text[];

-- Index so the Explore area filter (habitats @> '{tag}') is fast.
create index if not exists species_habitats_idx on public.species using gin (habitats);

-- Verify after enrichment:
--   select common_name, habitats from public.species where habitats is not null limit 20;
--   select unnest(habitats) tag, count(*) from public.species group by tag order by 2 desc;
