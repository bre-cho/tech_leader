# Backend API Contracts

## Endpoints Phase 1
- `POST /api/v1/design/generate`
- `POST /api/v1/design/score`
- `POST /api/v1/design/select`
- `POST /api/v1/upsell/analyze`
- `POST /api/v1/video/concept`

## Endpoints Phase 2
- `POST /api/v1/video/storyboard`
- `POST /api/v1/offers/recommend`
- `POST /api/v1/crm/followup`
- `GET /api/v1/dashboard/upsell`

## Endpoints Phase 3
- `POST /api/v1/memory/winner-dna`
- `GET /api/v1/memory/winner-dna/recall`
- `POST /api/v1/render/project`

## Standard Response
```json
{
  "ok": true,
  "trace_id": "uuid",
  "project_id": "uuid",
  "data": {},
  "warnings": [],
  "lineage": {
    "step": "image.scored",
    "parent_step_id": "uuid|null",
    "artifact_id": "uuid|null"
  }
}
```
