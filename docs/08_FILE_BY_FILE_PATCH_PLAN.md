# File-by-file Patch Plan

## Backend
- `backend/app/agents/contracts.py`: schema chung cho agent.
- `backend/app/agents/runtime.py`: Technical Lead orchestrator.
- `backend/app/agents/design_agents.py`: business/image/QA/industry/upsell/video/storyboard/offer/CRM/analytics/memory agents.
- `backend/app/api/v1/design.py`: design endpoints.
- `backend/app/api/v1/upsell.py`: upsell endpoints.
- `backend/app/api/v1/video.py`: concept/storyboard endpoints.
- `backend/app/api/v1/offers.py`: offer endpoints.
- `backend/app/api/v1/crm.py`: follow-up endpoints.
- `backend/app/api/v1/memory.py`: winner DNA endpoints.
- `backend/app/api/v1/dashboard.py`: upsell dashboard.
- `backend/app/models/design_to_video.py`: SQLAlchemy models.
- `backend/app/schemas/design_to_video.py`: Pydantic schemas.

## Frontend
- `frontend/app/design-studio/page.tsx`: main studio page.
- `frontend/components/design-studio/*`: UI sections.

## Governance
- `scripts/techlead_mvp_audit.py`: audit wrapper.
- `.github/workflows/design-to-video-release-gate.yml`: CI release gate.
