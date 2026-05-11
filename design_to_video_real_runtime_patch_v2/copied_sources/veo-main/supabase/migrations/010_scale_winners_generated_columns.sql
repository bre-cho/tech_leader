-- ─── scale_intelligence_winners: generated columns for upsert deduplication ──
--
-- Supabase-js upsert() only accepts plain column names in the onConflict
-- option – SQL expressions like md5(hook) are not supported.  Migration 009
-- created a unique index on (industry, md5(hook), md5(visual_concept)) which
-- cannot be referenced by name in the Supabase client.
--
-- This migration:
--   1. Drops the expression-based unique index from migration 009.
--   2. Adds two GENERATED ALWAYS AS STORED columns: hook_md5, visual_concept_md5.
--   3. Creates a new unique index on (industry, hook_md5, visual_concept_md5).
--
-- After this migration WinnerLearningEngine can use:
--   onConflict: "industry,hook_md5,visual_concept_md5"

-- 1. Drop the expression-based index added by migration 009.
drop index if exists public.idx_scale_winners_dedup;

-- 2. Add generated columns.
alter table public.scale_intelligence_winners
  add column if not exists hook_md5 text
    generated always as (md5(hook)) stored;

alter table public.scale_intelligence_winners
  add column if not exists visual_concept_md5 text
    generated always as (md5(visual_concept)) stored;

-- 3. Recreate the unique index using column names only.
create unique index if not exists idx_scale_winners_dedup
  on public.scale_intelligence_winners(industry, hook_md5, visual_concept_md5);
