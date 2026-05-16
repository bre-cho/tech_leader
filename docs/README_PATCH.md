# TECH_LEADER_CREATIVE_OS_MVP_FULL_PATCH

Nâng cấp MVP thành AI-Native Creative Production Operating System.

## Luồng chính

Creative Brief → Research Runtime → Image Source → Video Duration Planner → Provider Selector → Image Battle → Winner Selection → Storyboard Extraction → Timeline Composition → Provider Dispatch → Sequential Render Runtime → Delivery → Memory Learning.

## Luật render bắt buộc

- planned_batch_size = số cảnh trong một batch kế hoạch.
- max_concurrent_render = số cảnh được render đồng thời.
- Mặc định planned_batch_size = 6, max_concurrent_render = 1.
- Batch 01 có Scene 01–06 nhưng chỉ render Scene 01; Scene 01 xong mới render Scene 02.

## Cài đặt

Backend:
```python
from app.api.routes.creative_os import router as creative_os_router
app.include_router(creative_os_router, prefix="/api/v1")
```

Next.js: copy `frontend-next/app`, `frontend-next/components`, `frontend-next/types`, `frontend-next/lib`.

Vite: copy `frontend-vite/src` vào frontend Vite.

## API

- GET /api/v1/creative-os/provider-profiles
- POST /api/v1/creative-os/projects/{project_id}/plan-storyboard
- GET /api/v1/creative-os/projects/{project_id}/render-steps
- GET /api/v1/creative-os/projects/{project_id}/events
