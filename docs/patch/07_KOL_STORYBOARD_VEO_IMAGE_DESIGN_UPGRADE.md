# 07 — KOL Storyboard + Veo Image Design Upgrade Patch

## Mục tiêu

Patch này không chỉ copy khung sườn. Patch đã:

1. **Copy module thật từ `kol-main-4`** để nâng cấp `StoryboardAgent` thành Auto Storyboard Runtime có phân tích poster/brief, selling mechanism, camera motion, provider prompts và scorecard.
2. **Copy module thật từ `veo-main-7`** để nâng cấp `ImageDesignAgent` thành Poster Intelligence Runtime có mechanism detection, 3 variant trust/viral/conversion, prompt compiler, scoring, provider contract.
3. Giữ compatibility với MVP cũ: `/design-studio/run` vẫn trả về `storyboard: list[scene]` để frontend không vỡ.
4. Thêm endpoint debug/production handoff: `/api/v1/storyboard/full` để lấy đủ 3 storyboard variants.

---

## Module đã copy từ `kol-main-4`

Được đặt tại:

```text
backend/app/vendor/kol_storyboard_engine/
backend/app/vendor/kol_drama_runtime/
backend/app/vendor/kol_render_runtime/
```

Các phần quan trọng:

```text
storyboard_engine/
  camera_motion_engine.py
  mechanism_detector.py
  poster_analyzer.py
  prompt_compiler.py
  schemas.py
  scoring.py
  service.py
  storyboard_generator.py

cinematic_language_engine/
provider_adapters/
provider_scene_planner.py
storyboard_schema_legacy.py
storyboard_routes_source.py
```

### Logic được port vào `backend/app/agents/storyboard.py`

```text
Brief/Input
↓
Poster/Visual Analysis
↓
Selling Mechanism Detection
↓
Trust / Viral / Conversion Storyboard Variants
↓
Scene Timeline
↓
Camera + Motion Planning
↓
Provider Prompt Compile: Veo / Runway / Kling / Seedance2
↓
Scorecard
↓
Recommended Variant
```

---

## Module đã copy từ `veo-main-7`

Được đặt tại:

```text
backend/app/vendor/veo_v4_poster/
backend/app/vendor/veo_poster_intelligence/
backend/app/vendor/veo_ai_design_workforce/
backend/app/vendor/veo_poster_backend_packages/
```

Các phần quan trọng:

```text
v4-poster/
  engine.ts
  layout.ts
  mechanism.ts
  prompt-compiler.ts
  scoring.ts
  types.ts

prompt-v6/
prompt/
poster-intelligence/
poster-production/
ai-design-workforce/
creative-os/
poster-engine-backend/packages/
```

### Logic được port vào `backend/app/agents/image_design.py`

```text
Business Diagnosis
↓
Normalize Poster Input
↓
Selling Mechanism Detection
↓
Prompt Compiler
↓
Trust / Viral / Conversion Variants
↓
Attention / Trust / Conversion / Brand Fit Score
↓
Winner-ready Provider Contract
```

---

## API mới

### 1. Chạy workflow chính

```bash
curl -X POST http://localhost:8000/api/v1/design-studio/run \
  -H 'Content-Type: application/json' \
  -d '{
    "industry": "skincare beauty",
    "product": "premium serum",
    "audience": "women 25-40",
    "channel": "TikTok",
    "goal": "conversion",
    "brand_name": "LumiSkin"
  }'
```

### 2. Lấy đầy đủ 3 storyboard variants

```bash
curl -X POST http://localhost:8000/api/v1/storyboard/full \
  -H 'Content-Type: application/json' \
  -d '{
    "industry": "skincare beauty",
    "product": "premium serum",
    "audience": "women 25-40",
    "channel": "TikTok",
    "goal": "conversion",
    "brand_name": "LumiSkin"
  }'
```

---

## File cần dev review khi merge

```text
backend/app/agents/image_design.py
backend/app/agents/storyboard.py
backend/app/schemas/design.py
backend/app/api/routes.py
backend/app/vendor/**
```

---

## Kiểm tra nhanh

```bash
cd backend
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload
```

---

## Ghi chú production

Patch hiện đã vận hành thật theo logic deterministic, không phụ thuộc API key. Khi nối provider thật:

1. Image provider nhận `best_concept.prompt` + `negative_prompt`.
2. Video provider nhận `storyboard[n].provider_prompts.veo|runway|kling|seedance2`.
3. Sau khi render, lưu artifact vào `ContextGraphStore` + `WinnerDNAEngine`.
4. Promotion Gate chỉ cho scale nếu:

```text
image.score.conversion_score >= 85
storyboard.scorecard.final_score >= 85
video provider output validated
artifact contract valid
```
