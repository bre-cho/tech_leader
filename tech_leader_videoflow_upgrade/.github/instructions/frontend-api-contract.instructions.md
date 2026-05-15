---
description: "Use when editing frontend API client, request/response typing, or DesignStudio UI data mapping. Keeps frontend types synchronized with backend schema and avoids contract drift."
name: "Frontend API Contract Sync"
applyTo: "frontend/src/**/*"
---
# Frontend API Contract Sync

- Treat backend as source of truth for payload shape and field names.
- Keep frontend API types aligned with:
  - backend/app/schemas/design.py
  - frontend/src/lib/api.ts
- Do not rename request/response fields in frontend unless backend is updated in the same patch.
- If backend adds fields, update frontend types first, then UI usage.
- If backend makes fields optional/required, reflect the same optionality in frontend types.
- Keep API base and route assumptions consistent with:
  - /api/v1
  - VITE_API_BASE behavior in docker-compose
- When mapping server data to components, avoid silent fallback logic that can hide contract breaks.
- Add lightweight UI guards for null/undefined values, but do not mask schema mismatches.
- Before finishing frontend contract edits, run:
  - npm run build (from frontend)
