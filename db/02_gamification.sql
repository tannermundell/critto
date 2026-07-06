-- =====================================================================
-- Critto — gamification data (run once on your existing Supabase project)
-- Adds & populates: species.rarity  and  species.introduced
-- Safe to re-run (idempotent).
-- =====================================================================

-- ---------------------------------------------------------------------
-- Columns (added if they don't already exist)
-- ---------------------------------------------------------------------
alter table public.species add column if not exists rarity     text;
alter table public.species add column if not exists introduced boolean not null default false;


-- ---------------------------------------------------------------------
-- Rarity — the RARER of two signals:
--   (a) observation tier: how often the species is photographed in SA
--       (ranked WITHIN class, since birds are observed far more than reptiles).
--   (b) conservation floor: a minimum rarity based on IUCN status, so
--       threatened species can't come out "Common" just because they're
--       heavily photographed (the rhino problem).
-- Final rarity = the higher (rarer) of the two. Tiers are 1..5:
--   1 Common, 2 Uncommon, 3 Rare, 4 Very Rare, 5 Legendary.
-- Cutoffs and the IUCN mapping are tunable.
-- ---------------------------------------------------------------------
with ranked as (
    select id, iucn_status,
           percent_rank() over (partition by class order by sa_observations desc) as pr
    from public.species
),
tiers as (
    select id,
        -- (a) observation tier (most-observed = Common)
        case
            when pr <= 0.40 then 1
            when pr <= 0.65 then 2
            when pr <= 0.85 then 3
            when pr <= 0.95 then 4
            else                 5
        end as obs_tier,
        -- (b) conservation floor
        case iucn_status
            when 'Critically Endangered' then 5
            when 'Endangered'            then 4
            when 'Vulnerable'            then 3
            when 'Near Threatened'       then 3
            else                              1
        end as cons_floor
    from ranked
)
update public.species s
set rarity = (array['Common','Uncommon','Rare','Very Rare','Legendary'])[
                 greatest(t.obs_tier, t.cons_floor)
             ]
from tiers t
where t.id = s.id;


-- ---------------------------------------------------------------------
-- Introduced / "alien" flag — the clear-cut non-natives in our 150.
-- (House Sparrow and Eastern Gray Squirrel. Other classic SA aliens like
-- Common Myna / Mallard / Common Starling aren't in our current species set.)
-- ---------------------------------------------------------------------
update public.species
set introduced = true
where scientific_name in (
    'Passer domesticus',     -- House Sparrow
    'Sciurus carolinensis'   -- Eastern Gray Squirrel
);


-- ---------------------------------------------------------------------
-- Verify
-- ---------------------------------------------------------------------
-- Rarity spread per class:
--   select class, rarity, count(*) from public.species group by class, rarity order by class, rarity;
-- Spot-check the charismatic threatened species (should NOT be Common):
--   select common_name, iucn_status, rarity from public.species
--   where common_name in ('White Rhinoceros','Lion','Leopard','Cheetah','African Wild Dog','African Penguin');
-- Flagged aliens:
--   select common_name, scientific_name, class from public.species where introduced;
