# Source Audit — veo-main-7 Image Design Runtime

## Kết luận

`veo-main-7` có image/poster engine thật, gồm:

- `lib/v4-poster/engine.ts`: orchestrator tạo trust/viral/conversion variants.
- `lib/v4-poster/mechanism.ts`: detect selling mechanism.
- `lib/v4-poster/layout.ts`: chọn layout theo mechanism.
- `lib/v4-poster/prompt-compiler.ts`: compile prompt + negative prompt.
- `lib/v4-poster/scoring.ts`: score variant.
- `lib/poster-intelligence/*`: poster QA/auto-fix/CTR optimization.
- `poster-engine-backend/packages/*`: backend prompt engine, scoring engine, provider adapters, artifact contracts.

## Đã áp dụng vào MVP

- Port core v4-poster logic sang `backend/app/agents/image_design.py`.
- Copy nguyên source vào `backend/app/vendor/veo_v4_poster/`, `veo_poster_intelligence/`, `veo_ai_design_workforce/`, `veo_poster_backend_packages/`.
- Agent hiện tạo variant thật:
  - Trust
  - Viral
  - Conversion
- Mỗi variant có:
  - selling mechanism
  - layout direction
  - prompt
  - negative prompt
  - score
  - provider contract

## Không chỉ copy khung

Patch đã chuyển logic vận hành chính vào agent:

```text
normalize input → detect mechanism → compile prompt → score variants → rank winner
```
