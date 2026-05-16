# MVP_CREATIVE_OS_UIUX_FULL_PATCH

## Mục tiêu
Nâng cấp MVP thành AI Creative Production Operating System.

Luồng chính:
Creative Brief → Upload ảnh/ảnh AI tạo ra → nhập thời lượng video → chọn provider → tự tính số cảnh → tạo storyboard → chia batch kế hoạch → render tuần tự từng cảnh → Vite Video Studio → Delivery → Memory Learning.

## Luật render bắt buộc
- `planned_batch_size` = số cảnh nằm trong một batch kế hoạch.
- `max_concurrent_render` = số cảnh được render đồng thời.
- Mặc định: `planned_batch_size = 6`, `max_concurrent_render = 1`.
- Nếu Batch 01 có Scene 01–06 thì hệ thống vẫn chỉ render Scene 01; Scene 01 hoàn thiện mới render Scene 02.

## Kiến trúc
- Next.js = AI Project Operating System / Control Plane
- Vite = Realtime Cinematic Production Studio
- FastAPI = Orchestration Brain
- Celery = Execution Infrastructure
- VideoFlow = Timeline Composition Runtime

## Cách áp dụng
1. Copy `backend/app/creative_os` và `backend/app/api/routes/creative_os.py` vào backend.
2. Include router:
```python
from app.api.routes.creative_os import router as creative_os_router
app.include_router(creative_os_router, prefix="/api/v1")
```
3. Copy `frontend-next/*` vào root Next.js.
4. Copy `frontend-vite/src/*` vào Vite frontend.
5. Next.js env:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_VIDEO_STUDIO_URL=http://localhost:5173
```
