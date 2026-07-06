# Supabase setup — Phase 1

Two steps: create the schema, then seed the species table. ~5 minutes, no code.

## 1. Create the schema

1. Supabase dashboard → **SQL Editor** → **New query**.
2. Paste the contents of `schema.sql` and **Run**.
3. This creates the `species` and `sightings` tables, RLS policies, and the private `sightings` storage bucket.

## 2. Seed the species table (no-code CSV import)

The `species` table columns are aligned to `scripts/sa_species_list.csv`, so use Supabase's built-in import:

1. Dashboard → **Table Editor** → open the `species` table.
2. **Insert** → **Import data from CSV**.
3. Upload `scripts/sa_species_list.csv`.
4. Confirm the column mapping — these should line up automatically:
   `class, common_name, scientific_name, iucn_status, inat_taxon_id, sa_observations, photo_url`
   (`id`, `cached_entry`, `model_label`, `created_at` fill themselves — leave unmapped.)
5. Import. You should get **150 rows**.

## 3. Verify

Run in the SQL Editor:

```sql
select class, count(*) from public.species group by class;          -- expect 50 / 50 / 50
select count(*) from public.species where iucn_status is null;       -- expect 0
select common_name, iucn_status from public.species
  where iucn_status not in ('Least Concern') order by iucn_status;   -- the threatened ones
```

## 4. Gamification data (rarity + introduced)

After seeding, run `02_gamification.sql` in the SQL Editor. It adds and populates:
- `rarity` — Common → Legendary, ranked within class by observation count.
- `introduced` — flags non-native species (House Sparrow, Eastern Gray Squirrel).

Safe to re-run. Verify:

```sql
select class, rarity, count(*) from public.species group by class, rarity order by class, rarity;
select common_name, class from public.species where introduced;
```

## Notes

- **Re-importing:** if you need to redo the import, clear the table first: `truncate public.species cascade;`
- **`cached_entry`** stays empty until the knowledge agent fills it at runtime (the backend uses the service-role key, which bypasses RLS).
- **Alternative (SQL seed):** if you'd rather seed by script instead of the dashboard, say so and I'll add a generator that turns the CSV into a `seed.sql` of INSERT statements.
