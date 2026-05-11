-- Self-learning AI storage tables.
-- Replaces the previous file-based JSON store (data/self-learning-ai-store/).

create table if not exists public.learning_events (
  id uuid primary key default gen_random_uuid(),
  campaign_id text not null,
  variant_id text not null,
  dna jsonb not null default '{}'::jsonb,
  impressions integer not null default 0,
  clicks integer not null default 0,
  leads integer not null default 0,
  sales integer not null default 0,
  spend numeric not null default 0,
  revenue numeric not null default 0,
  predicted_score numeric not null default 0,
  qa_passed boolean not null default true,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_learning_events_campaign_id on public.learning_events(campaign_id);
create index if not exists idx_learning_events_created_at on public.learning_events(created_at asc);

create table if not exists public.learning_winner_dna (
  dna_id text primary key,
  campaign_id text not null,
  variant_id text not null,
  dna jsonb not null default '{}'::jsonb,
  performance jsonb not null default '{}'::jsonb,
  score numeric not null default 0,
  clone_count integer not null default 0,
  created_at bigint not null
);

create index if not exists idx_learning_winner_dna_score on public.learning_winner_dna(score desc);

create table if not exists public.learning_weight_model (
  id text primary key default 'singleton',
  version text not null default 'v1',
  weights jsonb not null default '{}'::jsonb,
  thresholds jsonb not null default '{}'::jsonb,
  sample_count integer not null default 0,
  updated_at timestamptz not null default now()
);
