# Project Guidelines

## Code Style
- Follow existing backend style in `backend/app`: small focused modules, explicit dict keys, and predictable return payloads.
- Keep API contracts aligned with `backend/app/schemas/design.py` and frontend usage in `frontend/src/lib/api.ts`.
- Prefer additive changes over broad refactors. Avoid renaming public response fields unless both backend and frontend are updated together.

## Architecture
- Core runtime flow is non-optional: `target_define -> research -> plan -> execute -> verify -> distill_to_skill -> memory_update -> winner_dna_update`.
- Route design-to-video features through `backend/app/runtime/orchestrator.py` and `backend/app/governance/operating_law.py`, not via standalone agent calls.
- Keep boundaries clear:
  - Backend orchestration and agents: `backend/app/runtime`, `backend/app/agents`
  - Governance and gates: `backend/app/governance`
  - Persistence and memory: `backend/app/models`, `backend/app/memory`, `backend/app/context_graph`
  - UI and API client: `frontend/src/pages/DesignStudio.tsx`, `frontend/src/lib/api.ts`

## Build and Test
- Backend setup and run:
  - `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
  - `uvicorn app.main:app --reload --port 8000`
- Frontend setup and run:
  - `cd frontend && npm install`
  - `npm run dev`
- Full stack Docker:
  - `docker compose up --build`
- Backend verification used by the project:
  - `scripts/verify_backend.sh` (runs `python -m compileall app` and `pytest -q`)

## Conventions
- Respect hard operating law in `backend/app/governance/operating_law.py`:
  - `NO WORKFLOW -> NO BUILD`
  - `NO VERIFY -> NO PROMOTION`
  - `NO MEMORY -> NO SCALE`
- For new features, follow checklist in `docs/patch/04_ADDING_NEW_FEATURE_RULE.md`.
- Promotion gate must remain driven by verification plus law trace (see `backend/app/runtime/orchestrator.py`).
- Winner DNA writes must keep threshold and dedupe behavior in `backend/app/memory/winner_dna.py`.
- Context graph updates should preserve required entities and relation shape from `backend/app/runtime/orchestrator.py` and `backend/app/context_graph/store.py`.

## Project Gotchas
- Default storage is SQLite via `DATABASE_URL=sqlite:///./agentic_creative.db`; concurrent writes can cause lock contention during heavy local runs.
- Frontend calls backend through `VITE_API_BASE` (see `docker-compose.yml`); keep backend on `:8000` and API prefix `/api/v1` unless both sides are updated.
- `AGENTIC_STRICT_MODE` defaults to true; do not add bypass paths that skip governance or verification.
- There is no `backend/app/services` layer currently; provider-related integrations are under `backend/app/vendor`.

## References
- Overview: `README.md`
- Backend architecture: `docs/01_BACKEND_ARCHITECTURE.md`
- Frontend guide: `docs/02_FRONTEND_PATCH_GUIDE.md`
- Operating law details: `docs/architecture/01_HARDCODE_OPERATING_LAW.md`
- Context graph details: `docs/architecture/02_CONTEXT_GRAPH.md`
- Provider integration notes: `docs/04_PROVIDER_INTEGRATION.md`
- Smoke tests and runbook: `docs/05_SMOKE_TESTS.md`, `docs/operations/03_RUNBOOK.md`
- Production hardening roadmap: `docs/06_PRODUCTION_HARDENING.md`
