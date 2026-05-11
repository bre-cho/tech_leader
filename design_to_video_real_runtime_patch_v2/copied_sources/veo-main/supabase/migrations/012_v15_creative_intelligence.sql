create extension if not exists pgcrypto;

do $$
begin
  if not exists (
    select 1
    from pg_type t
    join pg_namespace n on n.oid = t.typnamespace
    where t.typname = 'luxury_level'
      and n.nspname = 'public'
  ) then
    create type public.luxury_level as enum ('accessible', 'premium', 'ultra-luxury');
  end if;
end $$;

create table if not exists public.creative_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  input jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.creative_scores (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.creative_sessions(id) on delete cascade,
  luxury_score numeric(4, 3),
  editorial_score numeric(4, 3),
  trust_score numeric(4, 3),
  created_at timestamptz not null default now()
);

create table if not exists public.creative_layouts (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.creative_sessions(id) on delete cascade,
  layout text not null,
  spacing text not null,
  typography text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.brand_genomes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  logo_dna jsonb not null default '{}'::jsonb,
  color_dna jsonb not null default '{}'::jsonb,
  typography_dna jsonb not null default '{}'::jsonb,
  perception_dna jsonb not null default '{}'::jsonb,
  luxury_level public.luxury_level not null default 'premium',
  consistency_score numeric(4, 3) not null default 0.500,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists idx_brand_genomes_user_id on public.brand_genomes(user_id);

create table if not exists public.campaign_history (
  id uuid primary key default gen_random_uuid(),
  brand_genome_id uuid not null references public.brand_genomes(id) on delete cascade,
  campaign_direction text,
  results jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.typography_profiles (
  id uuid primary key default gen_random_uuid(),
  brand_genome_id uuid not null references public.brand_genomes(id) on delete cascade,
  family text not null,
  hierarchy jsonb not null default '{}'::jsonb,
  luxury_score numeric(4, 3),
  created_at timestamptz not null default now()
);

alter table public.creative_sessions enable row level security;
alter table public.creative_scores enable row level security;
alter table public.creative_layouts enable row level security;
alter table public.brand_genomes enable row level security;
alter table public.campaign_history enable row level security;
alter table public.typography_profiles enable row level security;

drop policy if exists "creative_sessions owner" on public.creative_sessions;
create policy "creative_sessions owner"
  on public.creative_sessions
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists "creative_scores owner" on public.creative_scores;
create policy "creative_scores owner"
  on public.creative_scores
  for all
  using (
    exists (
      select 1
      from public.creative_sessions s
      where s.id = creative_scores.session_id
        and s.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1
      from public.creative_sessions s
      where s.id = creative_scores.session_id
        and s.user_id = auth.uid()
    )
  );

drop policy if exists "creative_layouts owner" on public.creative_layouts;
create policy "creative_layouts owner"
  on public.creative_layouts
  for all
  using (
    exists (
      select 1
      from public.creative_sessions s
      where s.id = creative_layouts.session_id
        and s.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1
      from public.creative_sessions s
      where s.id = creative_layouts.session_id
        and s.user_id = auth.uid()
    )
  );

drop policy if exists "brand_genomes owner" on public.brand_genomes;
create policy "brand_genomes owner"
  on public.brand_genomes
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists "campaign_history owner" on public.campaign_history;
create policy "campaign_history owner"
  on public.campaign_history
  for all
  using (
    exists (
      select 1
      from public.brand_genomes g
      where g.id = campaign_history.brand_genome_id
        and g.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1
      from public.brand_genomes g
      where g.id = campaign_history.brand_genome_id
        and g.user_id = auth.uid()
    )
  );

drop policy if exists "typography_profiles owner" on public.typography_profiles;
create policy "typography_profiles owner"
  on public.typography_profiles
  for all
  using (
    exists (
      select 1
      from public.brand_genomes g
      where g.id = typography_profiles.brand_genome_id
        and g.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1
      from public.brand_genomes g
      where g.id = typography_profiles.brand_genome_id
        and g.user_id = auth.uid()
    )
  );