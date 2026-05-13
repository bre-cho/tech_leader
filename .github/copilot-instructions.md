# Project Guidelines

Use this workspace as a link-first map, not a second copy of the docs. Prefer the file paths below over re-describing behavior in new instructions.

## Start Here

- Repository overview: [README.md](README.md)
- Backend architecture: [docs/01_BACKEND_ARCHITECTURE.md](docs/01_BACKEND_ARCHITECTURE.md)
- Frontend patch guide: [docs/02_FRONTEND_PATCH_GUIDE.md](docs/02_FRONTEND_PATCH_GUIDE.md)
- Operating law: [docs/architecture/01_HARDCODE_OPERATING_LAW.md](docs/architecture/01_HARDCODE_OPERATING_LAW.md)
- Context graph: [docs/architecture/02_CONTEXT_GRAPH.md](docs/architecture/02_CONTEXT_GRAPH.md)
- Provider integration: [docs/04_PROVIDER_INTEGRATION.md](docs/04_PROVIDER_INTEGRATION.md)
- Smoke tests and runbook: [docs/05_SMOKE_TESTS.md](docs/05_SMOKE_TESTS.md), [docs/operations/03_RUNBOOK.md](docs/operations/03_RUNBOOK.md)
- Feature rules: [docs/patch/04_ADDING_NEW_FEATURE_RULE.md](docs/patch/04_ADDING_NEW_FEATURE_RULE.md)
- Production hardening: [docs/06_PRODUCTION_HARDENING.md](docs/06_PRODUCTION_HARDENING.md)

## Scoped Instructions

- Backend runtime changes: [backend runtime guard](.github/instructions/backend-runtime-guard.instructions.md)
- Runtime orchestrator and gate changes: [runtime orchestrator gate](.github/instructions/runtime-orchestrator-gate.instructions.md)
- Frontend API contract changes: [frontend API contract sync](.github/instructions/frontend-api-contract.instructions.md)
- Root Next.js UI changes: [root Next.js UI](.github/instructions/root-nextjs-ui.instructions.md)
- Frontend Vite workspace changes: [frontend Vite workspace](.github/instructions/frontend-vite-workspace.instructions.md)
- Frontend page mapping changes: [frontend pages mapping](.github/instructions/frontend-pages-mapping.instructions.md)
- Smoke test workflow: [smoke tests](.github/skills/smoke-tests/SKILL.md)
- Backend verification workflow: [backend verify](.github/skills/backend-verify/SKILL.md)

## Repo Shape

- Root Next.js app: `app/`, `components/`, `package.json`
- Backend API and runtime: `backend/app/`
- Separate Vite frontend workspace: `frontend/`
- Shared scripts and checks: `scripts/`, `tests/`
- Domain docs and audits: `docs/`, `context-graph/`, `memory/`

## Non-Negotiable Architecture

- The runtime lifecycle is fixed: `target_define -> research -> plan -> execute -> verify -> distill_to_skill -> memory_update -> winner_dna_update`.
- Design-to-video flow must go through `backend/app/runtime/orchestrator.py` and `backend/app/governance/operating_law.py`.
- Do not add shortcut paths that bypass verification, promotion gate logic, or law trace checks.
- Respect hard operating law in `backend/app/governance/operating_law.py`:
  - `NO WORKFLOW -> NO BUILD`
  - `NO VERIFY -> NO PROMOTION`
  - `NO MEMORY -> NO SCALE`
- Keep the boundaries clear:
  - Orchestration and agents: `backend/app/runtime`, `backend/app/agents`
  - Governance and gates: `backend/app/governance`
  - Persistence, memory, and context graph: `backend/app/models`, `backend/app/memory`, `backend/app/context_graph`
  - API schemas and client contract: `backend/app/schemas/design.py`, `frontend/src/lib/api.ts`
  - UI surfaces: `app/`, `components/`, `frontend/src/pages/DesignStudio.tsx`

## Contract Rules

- Treat backend schema as the source of truth for request and response shapes.
- Avoid renaming public fields unless backend and frontend are updated together in the same change.
- Keep promotion status driven by both verification results and law trace state.
- Preserve winner DNA threshold and dedupe behavior in `backend/app/memory/winner_dna.py`.
- Preserve required entities and relation shape in context graph writes from `backend/app/runtime/orchestrator.py` and `backend/app/context_graph/store.py`.
- If a change touches memory or context graph behavior, include the corresponding write path and verification update.

## Build And Test

- Backend setup and run:
  - `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
  - `uvicorn app.main:app --reload --port 8000`
- Backend verification:
  - `./scripts/verify_backend.sh`
- Root Next.js app:
  - `npm install`
  - `npm run dev`
  - `npm run build`
  - `npm run typecheck`
- Frontend workspace under `frontend/`:
  - `cd frontend && npm install`
  - `npm run dev`
  - `npm run build`
- Docker full stack:
  - `docker compose up --build`

## Project Gotchas

- Default storage is SQLite via `DATABASE_URL=sqlite:///./agentic_creative.db`; concurrent writes can lock under heavier local runs.
- `AGENTIC_STRICT_MODE` defaults to true; do not add bypass paths that skip governance or verification.
- Backend API routes are expected under `/api/v1`; keep `VITE_API_BASE` and docker-compose assumptions aligned unless both sides change together.
- There is no general `backend/app/services` layer; provider integrations live under `backend/app/vendor`.
- The repo contains both a root Next.js UI and a separate `frontend/` workspace; use the scripts and API client for the surface you are touching.

## When Adding Features

- Follow [docs/patch/04_ADDING_NEW_FEATURE_RULE.md](docs/patch/04_ADDING_NEW_FEATURE_RULE.md).
- For backend feature readiness, use the [feature-checklist skill](.github/skills/feature-checklist/SKILL.md).
- Prefer additive changes over broad refactors.
- Link to the relevant docs instead of repeating long explanations in new instructions.
