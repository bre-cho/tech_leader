# 11 — REAL RUNTIME PATCH PLAN

## P0 — Biến image generator từ mock sang thật

### Thêm image runtime bridge

File mới:

```txt
backend/app/services/real_image_provider_bridge.py
```

Nhiệm vụ:

- Nhận request từ `POST /api/v1/design/generate`.
- Compile prompt bằng logic `veo-main-7/lib/v4-poster` hoặc gọi poster-engine-backend.
- Gọi provider adapter thật.
- Lưu variant URL/path + metadata.
- Trả về image variants có `asset_url`, `provider`, `prompt`, `trace_id`.

### Frontend

`/design-studio` không hiển thị placeholder nữa. Bắt buộc hiển thị:

- trạng thái job tạo ảnh,
- ảnh thật từ `asset_url`,
- trace/scoring metadata.

## P1 — Biến video render từ mock sang thật

### Thêm video runtime bridge

File mới:

```txt
backend/app/services/real_video_render_bridge.py
```

Nhiệm vụ:

- Nhận storyboard từ Upsell/Storyboard Agent.
- Chuyển storyboard thành `RenderJobCreateRequest` của `kol-main-4`.
- Tạo scene tasks.
- Dispatch từng scene qua provider router.
- Poll hoặc nhận callback.
- Lưu artifact lineage.
- Gọi assembly/reassembly.

## P2 — Provider routing

Provider supported:

```txt
veo
veo_3
veo_3_1
runway
kling
seedance
seedance2
volcengine
```

Routing rule:

- Beauty/Fashion/F&B short ads → Runway/Kling/Seedance2.
- Cinematic tour/real estate → Veo/Runway.
- Product showcase → Kling/Seedance2.
- Story/narrative scene → Veo/Seedance.

## P3 — DB schema thật

Merge migrations từ:

```txt
copied_sources/kol-main/backend/alembic/versions/*render*.py
copied_sources/kol-main/backend/app/models/render_*.py
copied_sources/kol-main/backend/app/models/provider_*.py
copied_sources/veo-main/poster-engine-backend/migrations/versions/*.py
```

Cần bổ sung mapping vào MVP:

- `image_variants.asset_url`
- `image_variants.provider`
- `image_variants.provider_job_id`
- `video_concepts.source_image_variant_id`
- `video_storyboards.render_job_id`
- `winner_dna.source_artifact_id`

## P4 — Release gate

Không cho release nếu:

- Provider config thiếu trong production.
- API tạo ảnh vẫn trả placeholder.
- Render endpoint chỉ dry-run.
- Không có artifact lineage.
- Không có callback/poll status.
- Không có retry/recovery policy.
- Không có audit report.
