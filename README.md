# Agentic Creative Operating Environment — MVP Final

MVP này đã được viết lại theo **CORE HARD OPERATING LAW**:

`USER INPUT → TECHNICAL LEAD AGENT → PLANNER → CAPABILITY ROUTER → SPECIALIZED AGENTS → EXECUTION MANAGER → VERIFICATION ENGINE → PROMOTION GATE → MEMORY UPDATE → WINNER DNA ENGINE`

Không build feature rời rạc. Mọi tính năng mới bắt buộc đi qua:

`Workflow → Agent → Skill → Runtime → Verify → Memory → Winner DNA`

## Modules chính

- Backend FastAPI orchestration runtime
- Hardcoded Operating Law / Governance Gate
- Technical Lead Agent
- Planner / Capability Router / Execution Manager
- Specialized Agents: Business Diagnosis, Image Design, Image QA, Upsell, Video Concept, Storyboard, Offer
- Memory Engine + Winner DNA Recall
- Context Graph Entities + Relations
- Frontend Design Studio
- Docs patch cho dev trong `docs/`
- Smoke tests trong `backend/tests/`

## Run nhanh

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Docker:

```bash
docker compose up --build
```
