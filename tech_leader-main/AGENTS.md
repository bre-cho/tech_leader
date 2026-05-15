# AI Workforce Operating Rules — Live Trading MVP

## Hard laws
- NO AUDIT → NO PATCH
- NO RISK GUARD → NO EXECUTION
- NO CONTEXT GRAPH → NO ARCHITECTURE CLAIM
- NO RELEASE GATE GO → NO LIVE MONEY
- NO MAGIC NUMBER / IDEMPOTENCY KEY → NO BROKER ORDER

## Agent 16 command
```bash
python scripts/agent16_audit.py . --runtime --apply-safe-fixes --out reports/agent16_audit_report.md
```

## Patch order
1. P0 runtime blockers / live-trading safety / secrets / syntax
2. P1 CI failures / import-export / contract failures
3. P2 graph architecture / memory consistency / governance drift
4. P3 scaling / autonomous cognition improvements

## Claude Code / Cursor / Copilot rule
Patch file-by-file. Add tests. Run Agent 16 after every patch batch.

## CodeNomad Core Layer — Local AI Coding Runtime
- Mặc định mọi lệnh cục bộ phải chạy ở chế độ dry-run trước.
- Lệnh rủi ro cao cần approval token `APPROVE_LOCAL_EXECUTION`.
- Lệnh phá hệ thống như xóa root, force push, reset destructive phải bị chặn.
- Agent 16 phải tạo `docs/runtime/codenomad-plan.md` trước khi thực thi.
- Agent 16 phải tạo `docs/runtime/codenomad-runtime-report.md` sau khi chạy lệnh.
- Nếu terminal báo lỗi, Agent 16 phải tạo `docs/runtime/codenomad-healing-plan.md` và không được xóa test để né lỗi.
- Ưu tiên sửa nguyên nhân gốc, giữ kiến trúc gốc, không refactor ngoài phạm vi task.
