# CodeNomad Execution Plan

- Created at: `2026-05-13T12:16:58.982371+00:00`
- Task: smoke test codenomad core
- Goal: Biến Agent 16 thành trợ lý lập trình tự vận hành: hiểu dự án, lập kế hoạch, chạy lệnh an toàn, tự đọc lỗi và báo cáo nghiệm thu.
- Approval required: `True`

## Assumptions
- Giữ nguyên kiến trúc gốc, ưu tiên patch cộng thêm thay vì refactor lớn.
- Mọi lệnh có rủi ro cao phải dừng ở cổng phê duyệt.
- Không tự động deploy hoặc ghi đè dữ liệu sản xuất.
- Đã phát hiện một số vùng rủi ro: AGENTS.md: possible-secret-reference; ai_trading_brain/codenomad_core/context.py: destructive-command-or-sql; ai_trading_brain/codenomad_core/context.py: possible-secret-reference; ai_trading_brain/codenomad_core/safety.py: destructive-command-or-sql; ai_trading_brain/engineering_os/governance.py: destructive-command-or-sql

## Steps
### S1. Quét ngữ cảnh dự án
- Intent: Hiểu cấu trúc file, test, script và tài liệu trước khi sửa.
- Risk: `low`
- Requires approval: `False`
- Commands:
  - `python scripts/agent16_codenomad.py context --repo .`
- Files to touch:
  - `docs/runtime/codenomad-context.json`
- Validation:
  - Context JSON được tạo và có danh sách module/test/docs.
- Rollback:
  - Xóa docs/runtime/codenomad-context.json nếu cần.

### S2. Lập kế hoạch thực thi an toàn
- Intent: Chia việc thành bước nhỏ, có kiểm thử và rollback rõ ràng.
- Risk: `low`
- Requires approval: `False`
- Commands:
  - `python scripts/agent16_codenomad.py plan "smoke test codenomad core" --repo .`
- Files to touch:
  - `docs/runtime/codenomad-plan.md`
- Validation:
  - Plan có goal, files, commands, rollback, manual test.
- Rollback:
  - Xóa hoặc sửa docs/runtime/codenomad-plan.md.

### S3. Chạy kiểm tra nền
- Intent: Xác thực repo trước khi giao AI tự sửa lỗi.
- Risk: `low`
- Requires approval: `False`
- Commands:
  - `python -m pytest -q`
- Files to touch:
  - `docs/runtime/codenomad-runtime-report.md`
- Validation:
  - pytest/compile/typecheck pass hoặc có báo cáo lỗi rõ ràng.
- Rollback:
  - Không thay đổi source; chỉ cập nhật báo cáo runtime.

### S4. Tự sửa lỗi từ phản hồi terminal
- Intent: Khi lệnh test fail, phân loại lỗi và đề xuất hành động sửa an toàn.
- Risk: `medium`
- Requires approval: `True`
- Commands:
  - `python scripts/agent16_codenomad.py heal --repo . --last-report docs/runtime/codenomad-runtime-report.md`
- Files to touch:
  - `docs/runtime/codenomad-healing-plan.md`
- Validation:
  - Healing plan chỉ đề xuất thay đổi, không tự sửa destructive.
- Rollback:
  - Không áp dụng healing plan hoặc revert patch thủ công.

## Manual Test
- Chạy: python scripts/agent16_codenomad.py run "audit project" --repo . --dry-run
- Mở docs/runtime/codenomad-plan.md để kiểm tra kế hoạch.
- Chạy lại không dry-run cho các lệnh kiểm thử an toàn.
- Đọc docs/runtime/codenomad-runtime-report.md trước khi merge/deploy.
