-- ─── winner_dna_industry ─────────────────────────────────────────────────────
-- Replaces the MOCK_WINNER_DNA_DB hardcoded object in
-- lib/winner-dna-gate/data.ts so winner patterns survive deployments and
-- can be updated at runtime without code changes.

create table if not exists public.winner_dna_industry (
  id           uuid    primary key default gen_random_uuid(),
  dna_id       text    not null unique,
  industry     text    not null,
  hook         text    not null,
  visual_concept text  not null,
  cta          text    not null,
  icons        jsonb   not null default '[]'::jsonb,
  predicted_ctr text   not null default '',
  metadata     jsonb   not null default '{}'::jsonb,
  created_at   timestamptz not null default now()
);

create index if not exists idx_winner_dna_industry_industry
  on public.winner_dna_industry(industry);
create index if not exists idx_winner_dna_industry_dna_id
  on public.winner_dna_industry(dna_id);

-- Seed the four initial winners previously hardcoded in MOCK_WINNER_DNA_DB.
insert into public.winner_dna_industry
  (dna_id, industry, hook, visual_concept, cta, icons, predicted_ctr, metadata)
values
  (
    'beauty_winner_01', 'beauty',
    'Ultra high converting luxury lipstick ad poster',
    'Extreme close-up lips with split effect',
    'INBOX CHỌN MÀU THEO CÁ TÍNH',
    '["⚡ Lên màu tức thì","💧 Không khô môi","🔥 Cực kỳ nổi bật"]'::jsonb,
    '3.5%–4.8%',
    '{"template":"beauty_lipstick_split_luxury_v1","tested_variants":3,"winner_rate":"87%"}'::jsonb
  ),
  (
    'fnb_winner_01', 'fnb',
    'Low-angle fashion campaign photograph of a confident model holding a large watermelon juice',
    'Product dominance with low-angle perspective and exaggerated foreground',
    'ĐẶT NGAY – GIẢI NHIỆT HÔM NAY',
    '["🍉 Tươi mát","⚡ Bổ sung năng lượng","💧 Giải nhiệt tức thì"]'::jsonb,
    '2.8%–4.0%',
    '{"template":"fnb_watermelon_juice_low_angle_product_dominance_v1","tested_variants":3,"winner_rate":"82%"}'::jsonb
  ),
  (
    'fashion_winner_01', 'fashion',
    'Luxury sleepwear realistic editorial with natural imperfections',
    'Ultra photorealistic model in professional studio lighting with natural beauty',
    'INBOX TƯ VẤN SIZE & MẪU',
    '["✨ Ren cao cấp","🖤 Thiết kế tối giản","🌙 Mặc nhà sang trọng"]'::jsonb,
    '2.4%–3.5%',
    '{"template":"fashion_sleepwear_realistic_editorial_v1","tested_variants":3,"winner_rate":"79%"}'::jsonb
  ),
  (
    'general_winner_01', 'general',
    'Premium product with clear value proposition',
    'Clean commercial layout with strong product focus and direct CTA',
    'INBOX TƯ VẤN NGAY',
    '["✅ Chất lượng cao","🚀 Giao nhanh","💎 Ưu đãi hôm nay"]'::jsonb,
    '2.2%–3.2%',
    '{"template":"general_commercial_v1","tested_variants":3,"winner_rate":"75%"}'::jsonb
  )
on conflict (dna_id) do nothing;

-- ─── scale_intelligence_winners ──────────────────────────────────────────────
-- Replaces the file-based JSON store (data/winner-learning-store.json) used
-- by WinnerLearningEngine in lib/scale-intelligence/services.ts.

create table if not exists public.scale_intelligence_winners (
  id             uuid    primary key default gen_random_uuid(),
  campaign_id    text    not null,
  variant_id     text    not null,
  industry       text    not null,
  hook           text    not null,
  visual_concept text    not null,
  cta            text    not null,
  winner_score   numeric not null default 0,
  creative_dna   jsonb   not null default '{}'::jsonb,
  saved_at       bigint  not null,
  created_at     timestamptz not null default now()
);

create index if not exists idx_scale_winners_industry
  on public.scale_intelligence_winners(industry);
create index if not exists idx_scale_winners_score
  on public.scale_intelligence_winners(winner_score desc);
-- One winner per industry + hook + visual_concept combination (deduplication).
create unique index if not exists idx_scale_winners_dedup
  on public.scale_intelligence_winners(industry, md5(hook), md5(visual_concept));

-- ─── profiles + billing credits ──────────────────────────────────────────────
-- Supports lib/billing/credits.ts (add_credits / deduct_credits RPCs called
-- by the Stripe webhook and credit-charging middleware).

create table if not exists public.profiles (
  id         uuid    primary key,
  email      text,
  credits    integer not null default 0 check (credits >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.credit_ledger (
  id         uuid    primary key default gen_random_uuid(),
  user_id    uuid    not null references public.profiles(id) on delete cascade,
  delta      integer not null,
  reason     text    not null,
  job_id     text,
  created_at timestamptz not null default now()
);

create index if not exists idx_credit_ledger_user_id
  on public.credit_ledger(user_id);

-- RPC: add_credits
-- Upserts the profile row and appends a ledger entry.
create or replace function public.add_credits(
  p_user_id uuid,
  p_amount  integer,
  p_reason  text
)
returns integer
language plpgsql
security definer
as $$
declare
  new_balance integer;
begin
  insert into public.profiles(id, credits)
    values (p_user_id, greatest(0, p_amount))
    on conflict (id) do update
      set credits    = public.profiles.credits + greatest(0, p_amount),
          updated_at = now();

  insert into public.credit_ledger(user_id, delta, reason)
    values (p_user_id, greatest(0, p_amount), p_reason);

  select credits into new_balance
    from public.profiles
   where id = p_user_id;

  return new_balance;
end;
$$;

-- RPC: deduct_credits
-- Deducts credits atomically; raises an exception if the balance is
-- insufficient so callers can surface a clear 402 error.
create or replace function public.deduct_credits(
  p_user_id uuid,
  p_amount  integer,
  p_reason  text,
  p_job_id  text default null
)
returns integer
language plpgsql
security definer
as $$
declare
  current_balance integer;
  new_balance     integer;
begin
  select credits
    into current_balance
    from public.profiles
   where id = p_user_id
     for update;

  if not found then
    raise exception 'Profile not found for user %', p_user_id;
  end if;

  if current_balance < p_amount then
    raise exception
      'Insufficient credits: % available, % required',
      current_balance, p_amount;
  end if;

  update public.profiles
     set credits    = credits - p_amount,
         updated_at = now()
   where id = p_user_id;

  insert into public.credit_ledger(user_id, delta, reason, job_id)
    values (p_user_id, -p_amount, p_reason, p_job_id);

  select credits into new_balance
    from public.profiles
   where id = p_user_id;

  return new_balance;
end;
$$;
