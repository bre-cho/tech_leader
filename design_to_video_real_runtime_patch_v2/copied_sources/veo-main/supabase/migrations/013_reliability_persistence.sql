-- Wave 2 Reliability: durable persistence and idempotency primitives.

-- ─────────────────────────────────────────────────────────────────────────────
-- Brand memory (replaces in-process fallback on production paths)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.brand_memory (
  brand_id text primary key,
  visual_dna jsonb,
  campaign_history jsonb not null default '[]'::jsonb,
  top_hooks jsonb not null default '[]'::jsonb,
  audience_behavior jsonb not null default '[]'::jsonb,
  typography_systems jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_brand_memory_updated_at
  on public.brand_memory(updated_at desc);

-- ─────────────────────────────────────────────────────────────────────────────
-- Poster production traces (durable trace backend)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.poster_production_traces (
  run_id uuid primary key,
  input_hash text not null,
  created_at timestamptz not null default now(),
  input jsonb not null,
  status text not null,
  module_trace jsonb not null default '[]'::jsonb,
  winner_variant_id text,
  qa_result jsonb,
  render_artifact_id text,
  performance_event_id text,
  render_contract jsonb
);

create index if not exists idx_poster_production_traces_created_at
  on public.poster_production_traces(created_at desc);

create index if not exists idx_poster_production_traces_input_hash
  on public.poster_production_traces(input_hash);

-- ─────────────────────────────────────────────────────────────────────────────
-- Scale-intelligence DLQ (durable dead-letter queue)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.scale_intelligence_dlq (
  id uuid primary key default gen_random_uuid(),
  campaign_id text not null,
  variant_id text not null,
  industry text not null,
  hook text not null,
  visual_concept text not null,
  cta text not null,
  winner_score double precision not null,
  creative_dna jsonb not null,
  saved_at bigint not null,
  error_message text not null,
  retry_count integer not null default 0,
  status text not null default 'pending',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_scale_intelligence_dlq_status_created_at
  on public.scale_intelligence_dlq(status, created_at desc);

-- ─────────────────────────────────────────────────────────────────────────────
-- Generic API idempotency records
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.api_idempotency_records (
  id uuid primary key default gen_random_uuid(),
  route text not null,
  method text not null,
  idempotency_key text not null,
  request_hash text not null,
  status text not null default 'processing',
  response_status integer,
  response_body jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(route, method, idempotency_key)
);

create index if not exists idx_api_idempotency_records_created_at
  on public.api_idempotency_records(created_at desc);
