# 09 — REAL RUNTIME INTEGRATION ANALYSIS

## Mục tiêu bản patch

Bản trước chỉ có scaffold MVP. Bản này đã **copy nguyên khối module vận hành thật** từ:

- `kol-main-4`: auto video render thật, provider routing, callback, polling, render job, artifact lineage, manifest, smart reassembly, subtitle burn-in, provider adapters cho Veo / Runway / Kling / Seedance / Seedance2.
- `veo-main-7`: provider tạo ảnh/poster thật, poster engine backend, prompt engine, scoring engine, export engine, image upscale, creative intelligence, poster production orchestration.

## Kết luận audit nguồn

### kol-main-4 có thể dùng làm video runtime thật

Các cụm đã copy:

- `backend/app/providers/**`
  - Adapter chuẩn hóa provider video.
  - Provider factory.
  - Veo adapter.
  - Runway adapter.
  - Kling adapter.
  - Seedance adapter.
  - Seedance2 adapter.
  - Callback/health/payload builders.

- `backend/app/api/*render*`, `backend/app/api/*provider*`, `backend/app/api/storyboard_routes.py`, `backend/app/api/video_router.py`
  - API tạo job render.
  - API trạng thái render.
  - API callback provider.
  - API payload preview.
  - API render dashboard.
  - API recovery.

- `backend/app/services/render_*`, `backend/app/services/provider_router.py`
  - Orchestrator render.
  - Dispatch/poll lifecycle.
  - Provider routing.
  - Job health.
  - Incident/work surface.

- `backend/app/render/**`
  - Assembly.
  - Manifest.
  - Dependency graph.
  - Reassembly.
  - Rerender.
  - Timeline drift guard.
  - Subtitle service.

- `backend/app/models/render_*`, `backend/app/models/provider_*`
  - DB models cho render jobs, scene tasks, provider audit, artifact lineage, rebuild audit.

### veo-main-7 có thể dùng làm image/poster provider thật

Các cụm đã copy:

- `poster-engine-backend/**`
  - FastAPI poster backend.
  - DB migrations.
  - provider adapters.
  - prompt engine.
  - scoring engine.
  - export engine.
  - image upscale.
  - worker/celery.
  - tests.

- `app/api/image/generate`
  - Next API route tạo ảnh.

- `app/api/poster-production/run`
  - Orchestration poster production.

- `app/api/poster-intelligence/**`
  - QA check.
  - CTR optimize.
  - Poster-to-video intelligence.
  - Auto-fix.

- `lib/v4-poster/**`
  - Engine tạo prompt poster theo mechanism, layout, scoring.

- `lib/poster-production/**`
  - Poster production orchestrator và traces.

- `lib/scoring/**`
  - Advanced scoring.

## Kiến trúc mới sau tích hợp

```txt
/design-studio
  ↓
Design Generate API
  ↓
Veo Poster/Image Runtime Bridge
  ↓
veo-main-7 poster-engine-backend + Next image API
  ↓
Image Scoring + Poster Intelligence
  ↓
Upsell Opportunity Agent
  ↓
Video Concept + Storyboard Agent
  ↓
KOL Video Render Bridge
  ↓
kol-main-4 provider router
  ↓
Veo / Runway / Kling / Seedance / Seedance2
  ↓
Render Job + Scene Task + Provider Callback + Polling
  ↓
Assembly / Subtitle / Manifest / Artifact Lineage
  ↓
Winner DNA Memory
```

## Không còn là scaffold ở các phần sau

- Tạo ảnh: dùng source thật từ `veo-main-7`.
- Chấm ảnh: dùng scoring/poster intelligence thật từ `veo-main-7`.
- Poster-to-video intelligence: dùng route/service thật từ `veo-main-7`.
- Auto video render: dùng provider runtime thật từ `kol-main-4`.
- Provider routing: dùng `provider_router`, `ProviderRouterClient`, adapters thật.
- Callback/polling: dùng module callback/status/poll thật.
- Assembly/reassembly/subtitle/manifest: dùng module render thật từ `kol-main-4`.

## Phần vẫn cần cấu hình khóa thật

Các module đã copy đủ, nhưng muốn gọi provider thật phải cấu hình `.env`:

- Veo / Google provider credentials.
- Runway API key.
- Kling API key/token.
- Seedance / Volcengine credentials.
- Redis.
- Postgres.
- Object storage nếu muốn public artifact URLs.

Nếu thiếu khóa, hệ nên chạy ở `dry_run/mock disabled carefully` hoặc trả lỗi provider config, không được giả vờ thành công trong production.
