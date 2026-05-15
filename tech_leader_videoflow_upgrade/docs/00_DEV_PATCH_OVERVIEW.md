# Dev Patch Overview — MVP Final

Patch này viết lại MVP theo core law bắt buộc:

`USER INPUT → TECHNICAL LEAD AGENT → PLANNER → CAPABILITY ROUTER → SPECIALIZED AGENTS → EXECUTION MANAGER → VERIFICATION ENGINE → PROMOTION GATE → MEMORY UPDATE → WINNER DNA ENGINE`

## Thay đổi chính

1. Thêm `backend/app/governance/operating_law.py` để hardcode operating law.
2. Thêm `Planner`, `CapabilityRouter`, `VerificationEngine`, `SkillDistiller`.
3. Viết lại `TechnicalLeadOrchestrator` để mọi workflow phải đi qua đủ lifecycle.
4. Thêm Context Graph đủ entity bắt buộc.
5. Thêm Winner DNA store/recall có threshold.
6. Frontend `/design-studio` hiển thị plan, scoring, upsell, storyboard, offer, promotion gate.
7. Tests kiểm tra promotion gate và law trace.

## Patch order

1. Copy `backend/` vào service backend.
2. Copy `frontend/` vào app studio hoặc tích hợp component `DesignStudio.tsx`.
3. Chạy backend tests.
4. Chạy frontend build.
5. Nếu merge vào repo cũ, ưu tiên giữ endpoint `/api/v1/design-studio/run` để không phá UI.
