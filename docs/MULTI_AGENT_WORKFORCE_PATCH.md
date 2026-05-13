# Multi-Agent Workforce Patch

Image Design Agent is split into a real workforce:

1. Creative Director Agent
2. Visual Strategist Agent
3. Composition Agent
4. Typography Agent
5. Brand Consistency Agent
6. Conversion Optimization Agent
7. Motion Thinking Agent
8. Industry Intelligence Agent
9. Design QA Agent

## API

```bash
POST /api/v1/workforce/image-design/run
```

## Run backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest -q
```

## Run frontend

Copy `frontend/app/image-design-workforce/page.tsx` into your Next.js app, then open:

```text
/image-design-workforce
```

## Design Rule

No single agent may generate final output directly.

All creative output must pass:

```text
Industry → Creative Direction → Visual Strategy → Brand → Composition → Typography → Conversion → Motion → QA
```
