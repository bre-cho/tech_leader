# 10 — FILE COPY MAP: MODULE THẬT ĐÃ COPY

## A. Video auto render thật từ `kol-main-4`

Đã copy vào:

```txt
copied_sources/kol-main/backend/app/
copied_sources/kol-main/backend/alembic/
copied_sources/kol-main/backend/alembic.ini
copied_sources/kol-main/requirements.txt
copied_sources/kol-main/.env.example
copied_sources/kol-main/.env.production.example
```

### Nhóm file chính cần merge vào backend MVP

```txt
backend/app/providers/**
backend/app/api/kling_provider.py
backend/app/api/runway_provider.py
backend/app/api/seedance_provider.py
backend/app/api/seedance2_provider.py
backend/app/api/provider_callbacks.py
backend/app/api/provider_payload_preview.py
backend/app/api/render_execution.py
backend/app/api/render_job_status.py
backend/app/api/render_events.py
backend/app/api/render_dashboard.py
backend/app/api/render_recovery.py
backend/app/api/render_quality.py
backend/app/api/production_render_routes.py
backend/app/api/poster_video_render_routes.py
backend/app/api/storyboard_routes.py
backend/app/api/video_router.py
backend/app/api/v1/provider_adapters.py
backend/app/services/render_orchestrator.py
backend/app/services/render_plan.py
backend/app/services/render_poll_service.py
backend/app/services/provider_router.py
backend/app/render/**
backend/app/media/video_merger.py
backend/app/models/render_*.py
backend/app/models/provider_*.py
backend/app/schemas/provider_*.py
backend/app/schemas/render_*.py
```

## B. Image/poster provider thật từ `veo-main-7`

Đã copy vào:

```txt
copied_sources/veo-main/poster-engine-backend/**
copied_sources/veo-main/app/api/image/**
copied_sources/veo-main/app/api/image-upscale/**
copied_sources/veo-main/app/api/poster-intelligence/**
copied_sources/veo-main/app/api/poster-production/**
copied_sources/veo-main/app/api/scoring/**
copied_sources/veo-main/lib/v4-poster/**
copied_sources/veo-main/lib/poster-intelligence/**
copied_sources/veo-main/lib/poster-production/**
copied_sources/veo-main/lib/scoring/**
copied_sources/veo-main/supabase/migrations/**
```

### Nhóm file chính cần merge vào frontend/Next app

```txt
app/api/image/generate/route.ts
app/api/image-upscale/route.ts
app/api/poster-intelligence/*/route.ts
app/api/poster-production/run/route.ts
app/api/poster-production/traces/route.ts
app/api/scoring/route.ts
lib/v4-poster/**
lib/poster-intelligence/**
lib/poster-production/**
lib/scoring/**
```

### Nhóm file chính cần merge vào backend Python nếu chạy poster engine riêng

```txt
poster-engine-backend/apps/api/main.py
poster-engine-backend/apps/api/image_upscale.py
poster-engine-backend/apps/api/creative_intelligence.py
poster-engine-backend/apps/api/fashion_poster_factory.py
poster-engine-backend/packages/provider_adapters/**
poster-engine-backend/packages/prompt_engine/**
poster-engine-backend/packages/scoring_engine/**
poster-engine-backend/packages/export_engine/**
poster-engine-backend/packages/contracts/**
poster-engine-backend/packages/fashion_poster_factory/**
poster-engine-backend/migrations/**
```

## C. Merge policy

Không copy đè mù toàn repo. Merge theo thứ tự:

1. Copy provider contracts/schema trước.
2. Copy provider adapters.
3. Copy render models/migrations.
4. Copy render services.
5. Copy render APIs.
6. Copy poster/image engine.
7. Wire route registry/main app.
8. Wire frontend `/design-studio` gọi API thật.
9. Chạy audit gate.
