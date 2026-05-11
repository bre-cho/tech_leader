# Bộ lệnh dùng trực tiếp cho Claude Code / Cursor / Copilot

## Lệnh 1 — Build Phase 1
```text
Bạn là Technical Lead Agent. Hãy implement Phase 1 cho MVP Design-to-Video Multi-Agent System theo docs/00-06. Không refactor kiến trúc gốc. Chỉ thêm module additive. Tạo endpoint design generate/score/select, upsell analyze, video concept. Mỗi agent output phải có trace_id, project_id, confidence_score, lineage. Sau khi code xong chạy syntax scan, import scan, test cơ bản và cập nhật docs/PATCH_REPORT.md.
```

## Lệnh 2 — Build Phase 2
```text
Tiếp tục implement Phase 2: storyboard generator, video package offer, CRM follow-up, upsell dashboard. Tất cả output phải lưu DB và có workflow_events. Không được mock leakage ở production path. Tạo tests cho API contract.
```

## Lệnh 3 — Build Phase 3
```text
Tiếp tục implement Phase 3: auto video project creation, winner DNA memory, industry playbooks, recall logic. Nếu chưa có render provider thật thì tạo provider adapter interface, không hard-code provider.
```

## Lệnh 4 — Audit toàn hệ
```text
Chạy Tech Lead Audit Agent theo docs/06_TECHLEAD_AUDIT_PROTOCOL.md. Quét syntax/import/type/dependency/logic/backend/frontend/worker/API/test/migration/CI/build. Xuất GO/NO-GO và file-by-file patch plan.
```

## Lệnh 5 — Release Gate
```text
Chỉ cho phép GO nếu npm build, pytest, alembic heads, API contract validation, graph integrity, memory consistency và replay validation đều pass. Nếu fail, tạo P0/P1/P2/P3 patch plan.
```
