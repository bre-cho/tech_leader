# APPLY_REAL_PROVIDER_RUNTIME

## Vai trò

Bạn là Technical Lead Agent. Nhiệm vụ: thay toàn bộ scaffold/mock của Design-to-Video MVP bằng runtime thật đã copy từ `kol-main-4` và `veo-main-7`.

## Luật bắt buộc

- Không được chỉ tạo skeleton.
- Không được trả ảnh placeholder nếu `IMAGE_GENERATION_REQUIRED=true`.
- Không được render dry-run trong production.
- Không được bỏ qua provider callback/polling.
- Không được release nếu không có artifact lineage.

## Thứ tự patch

1. Merge `copied_sources/veo-main/poster-engine-backend` hoặc Next image routes vào image runtime.
2. Merge `copied_sources/kol-main/backend/app/providers/**` vào backend/app/providers.
3. Merge `copied_sources/kol-main/backend/app/services/provider_router.py` và render services.
4. Merge render models + migrations.
5. Copy integration bridge:
   - `integrations/backend/app/services/real_image_provider_bridge.py`
   - `integrations/backend/app/services/real_video_render_bridge.py`
   - `integrations/backend/app/api/v1/design_to_video_real_pipeline.py`
6. Register router trong FastAPI app.
7. Update `/design-studio` gọi:
   - `/api/v1/real-pipeline/design/generate-real`
   - `/api/v1/real-pipeline/video/render-real`
8. Chạy:

```bash
python integrations/scripts/verify_real_runtime_imports.py
python scripts/techlead_mvp_audit.py
pytest
npm run build
```

## Output bắt buộc

- File-by-file patch summary.
- Import report.
- API smoke test result.
- GO/NO-GO release gate.
