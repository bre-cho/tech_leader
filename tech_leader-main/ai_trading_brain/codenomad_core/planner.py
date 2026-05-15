from __future__ import annotations

from pathlib import Path
from .models import ExecutionPlan, ExecutionStep, utc_now
from .context import scan_project_context
from .safety import classify_command


def _detect_validation_commands(root: Path) -> list[str]:
    commands: list[str] = []
    if (root / "pytest.ini").exists() or (root / "tests").exists():
        commands.append("python -m pytest -q")
    if (root / "package.json").exists():
        commands.append("npm test -- --runInBand")
    if not commands:
        commands.append("python -m py_compile scripts/*.py")
    return commands


def create_codenomad_plan(task: str, repo_root: str | Path = ".") -> ExecutionPlan:
    root = Path(repo_root).resolve()
    context = scan_project_context(root)
    validation_commands = _detect_validation_commands(root)
    risk_notes = context.risk_summary[:5]
    assumptions = [
        "Giữ nguyên kiến trúc gốc, ưu tiên patch cộng thêm thay vì refactor lớn.",
        "Mọi lệnh có rủi ro cao phải dừng ở cổng phê duyệt.",
        "Không tự động deploy hoặc ghi đè dữ liệu sản xuất.",
    ]
    if risk_notes:
        assumptions.append("Đã phát hiện một số vùng rủi ro: " + "; ".join(risk_notes))

    steps = [
        ExecutionStep(
            id="S1",
            title="Quét ngữ cảnh dự án",
            intent="Hiểu cấu trúc file, test, script và tài liệu trước khi sửa.",
            commands=["python scripts/agent16_codenomad.py context --repo ."],
            files_to_touch=["docs/runtime/codenomad-context.json"],
            risk="low",
            validation=["Context JSON được tạo và có danh sách module/test/docs."],
            rollback=["Xóa docs/runtime/codenomad-context.json nếu cần."],
        ),
        ExecutionStep(
            id="S2",
            title="Lập kế hoạch thực thi an toàn",
            intent="Chia việc thành bước nhỏ, có kiểm thử và rollback rõ ràng.",
            commands=["python scripts/agent16_codenomad.py plan \"%s\" --repo ." % task.replace('"', "'")],
            files_to_touch=["docs/runtime/codenomad-plan.md"],
            risk="low",
            validation=["Plan có goal, files, commands, rollback, manual test."],
            rollback=["Xóa hoặc sửa docs/runtime/codenomad-plan.md."],
        ),
        ExecutionStep(
            id="S3",
            title="Chạy kiểm tra nền",
            intent="Xác thực repo trước khi giao AI tự sửa lỗi.",
            commands=validation_commands,
            files_to_touch=["docs/runtime/codenomad-runtime-report.md"],
            risk="low",
            validation=["pytest/compile/typecheck pass hoặc có báo cáo lỗi rõ ràng."],
            rollback=["Không thay đổi source; chỉ cập nhật báo cáo runtime."],
        ),
        ExecutionStep(
            id="S4",
            title="Tự sửa lỗi từ phản hồi terminal",
            intent="Khi lệnh test fail, phân loại lỗi và đề xuất hành động sửa an toàn.",
            commands=["python scripts/agent16_codenomad.py heal --repo . --last-report docs/runtime/codenomad-runtime-report.md"],
            files_to_touch=["docs/runtime/codenomad-healing-plan.md"],
            risk="medium",
            validation=["Healing plan chỉ đề xuất thay đổi, không tự sửa destructive."],
            rollback=["Không áp dụng healing plan hoặc revert patch thủ công."],
            requires_approval=True,
        ),
    ]
    approval_required = any(step.requires_approval or classify_command(cmd).requires_approval for step in steps for cmd in step.commands)
    return ExecutionPlan(
        task=task,
        created_at=utc_now(),
        repo_root=str(root),
        goal="Biến Agent 16 thành trợ lý lập trình tự vận hành: hiểu dự án, lập kế hoạch, chạy lệnh an toàn, tự đọc lỗi và báo cáo nghiệm thu.",
        assumptions=assumptions,
        steps=steps,
        manual_test=[
            "Chạy: python scripts/agent16_codenomad.py run \"audit project\" --repo . --dry-run",
            "Mở docs/runtime/codenomad-plan.md để kiểm tra kế hoạch.",
            "Chạy lại không dry-run cho các lệnh kiểm thử an toàn.",
            "Đọc docs/runtime/codenomad-runtime-report.md trước khi merge/deploy.",
        ],
        approval_required=approval_required,
    )
