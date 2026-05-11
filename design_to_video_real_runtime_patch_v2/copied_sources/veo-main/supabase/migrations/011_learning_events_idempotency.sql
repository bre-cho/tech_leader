-- ─── learning_events: optional idempotency key ───────────────────────────────
--
-- P15: Adds an optional event_key column to learning_events.  When a caller
-- supplies a stable idempotency key (e.g. a hash of campaign_id + variant_id
-- + observation window) an ON CONFLICT DO NOTHING on this column prevents
-- duplicate rows if the same event is submitted more than once (e.g. due to
-- a network timeout and retry).
--
-- The column is nullable so that events without an idempotency key are
-- unaffected.

alter table public.learning_events
  add column if not exists event_key text;

create unique index if not exists idx_learning_events_event_key
  on public.learning_events(event_key)
  where event_key is not null;
