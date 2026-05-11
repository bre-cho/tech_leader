# Design-to-Video Multi-Agent MVP — Real Runtime Patch

Bản này thay hướng scaffold bằng cách copy module vận hành thật từ 2 repo nguồn:

- `kol-main-4` → auto video render thật với Veo / Runway / Kling / Seedance / Seedance2.
- `veo-main-7` → provider tạo ảnh/poster thật + scoring + poster intelligence.

## Thư mục quan trọng

```txt
copied_sources/kol-main/        # source thật render/video provider
copied_sources/veo-main/        # source thật image/poster provider
integrations/backend/           # bridge để nối MVP với source thật
docs/09-12                      # phân tích + file copy map + patch plan + env
.ai-workforce/commands/         # lệnh dùng trực tiếp cho Claude/Cursor/Copilot
```

## Cách áp dụng nhanh

1. Đọc `docs/09_REAL_RUNTIME_INTEGRATION_ANALYSIS.md`.
2. Merge theo `docs/10_FILE_COPY_MAP_REAL_MODULES.md`.
3. Làm theo `docs/11_REAL_RUNTIME_PATCH_PLAN.md`.
4. Cấu hình `.env` theo `docs/12_ENV_AND_PROVIDER_CONFIG.md`.
5. Dùng `.ai-workforce/commands/APPLY_REAL_PROVIDER_RUNTIME.md` để giao cho Claude Code/Cursor/Copilot patch vào repo chính.

## API mới được đề xuất

```txt
POST /api/v1/real-pipeline/design/generate-real
POST /api/v1/real-pipeline/video/render-real
```

Hai API này không thay thế API cũ ngay lập tức; chúng là integration bridge để chuyển dần từ MVP scaffold sang runtime thật.
