# DEV PATCH GUIDE

## 1. Copy backend

Copy:
- backend/app/creative_os
- backend/app/api/routes/creative_os.py

## 2. Copy Next.js

Copy:
- frontend-next/app
- frontend-next/components
- frontend-next/types
- frontend-next/lib

## 3. Copy Vite

Copy:
- frontend-vite/src/pages/DesignStudioCreativeOS.tsx
- frontend-vite/src/creative-os
- frontend-vite/src/styles/creative-os.css

## 4. Test planner

```bash
curl -X POST http://localhost:8000/api/v1/creative-os/projects/demo/plan-storyboard \
  -H "Content-Type: application/json" \
  -d '{"image_source":"upload","image_url":"/uploads/demo.png","target_video_duration":60,"provider":"kling","planned_batch_size":6,"max_concurrent_render":1}'
```

Expected:
- scene_count = 12
- scene_duration = 5
- planned_batch_size = 6
- max_concurrent_render = 1
- total_batches = 2
- execution_mode = sequential
