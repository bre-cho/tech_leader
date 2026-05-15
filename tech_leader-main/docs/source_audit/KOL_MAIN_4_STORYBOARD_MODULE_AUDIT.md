# Source Audit — kol-main-4 Storyboard Runtime

## Kết luận

`kol-main-4` có module storyboard thật, gồm:

- `storyboard_engine/poster_analyzer.py`: phân tích brief/poster theo ngành.
- `storyboard_engine/mechanism_detector.py`: phát hiện selling mechanism.
- `storyboard_engine/storyboard_generator.py`: tạo timeline 15s/30s, scene goal, visual, action, camera, motion.
- `storyboard_engine/prompt_compiler.py`: compile provider prompt cho Veo, Runway, Kling, Seedance.
- `storyboard_engine/scoring.py`: chấm CTR, attention, trust, conversion, final verdict.
- `storyboard_engine/service.py`: service runtime, timeout guard.

## Đã áp dụng vào MVP

- Port runtime sang `backend/app/agents/storyboard.py`.
- Copy nguyên source vào `backend/app/vendor/kol_storyboard_engine/` để dev đối chiếu/mở rộng.
- Giữ output legacy để frontend cũ không vỡ.
- Thêm `execute_full()` để trả full storyboard variants.

## Không chỉ copy khung

Patch đã chuyển logic vận hành chính vào agent:

```text
analyze poster → detect mechanism → generate variants → compile provider prompts → score → recommend
```
