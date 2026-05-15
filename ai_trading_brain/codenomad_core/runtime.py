from __future__ import annotations

import json
from pathlib import Path
from .context import scan_project_context, write_context
from .executor import run_command
from .healing import build_healing_plan
from .memory import append_session_memory
from .models import RuntimeReport, utc_now
from .planner import create_codenomad_plan


def ensure_codenomad_docs(repo_root: str | Path) -> None:
    root = Path(repo_root).resolve()
    for rel in ["docs/runtime", "docs/codenomad_core", ".codenomad_core"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    defaults = {
        "docs/codenomad_core/README.md": "# Agent 16 CodeNomad Core\n\nLõi này giúp Agent 16 quét ngữ cảnh dự án, lập kế hoạch, chạy lệnh an toàn, đọc lỗi terminal và ghi báo cáo nghiệm thu.\n",
        "docs/codenomad_core/LOCAL_EXECUTION_POLICY.md": "# Chính sách chạy lệnh cục bộ\n\n- Mặc định dry-run.\n- Lệnh rủi ro cao cần token phê duyệt.\n- Lệnh phá hệ thống bị chặn.\n- Không tự deploy, không tự push force.\n",
    }
    for rel, content in defaults.items():
        path = root / rel
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def run_codenomad_runtime(task: str, repo_root: str | Path = ".", dry_run: bool = True, approval_token: str | None = None) -> RuntimeReport:
    root = Path(repo_root).resolve()
    ensure_codenomad_docs(root)
    context = scan_project_context(root)
    context_path = write_context(context, root / "docs/runtime/codenomad-context.json")
    plan = create_codenomad_plan(task, root)
    plan_path = root / "docs/runtime/codenomad-plan.md"
    plan_path.write_text(plan.to_markdown(), encoding="utf-8")

    results = []
    for step in plan.steps:
        for command in step.commands:
            results.append(run_command(command, root, dry_run=dry_run, approval_token=approval_token))

    passed = all(r.status in {"executed", "skipped"} and (r.return_code in {0, None}) for r in results)
    healing_attempts = []
    if not passed:
        healing_path = root / "docs/runtime/codenomad-healing-plan.md"
        report_preview = RuntimeReport(task, str(plan_path), str(context_path), results, [], False, [], utc_now())
        temp_report = root / "docs/runtime/codenomad-runtime-report.md"
        temp_report.write_text(report_preview.to_markdown(), encoding="utf-8")
        healing_path.write_text(build_healing_plan(temp_report), encoding="utf-8")
        healing_attempts.append({"healing_plan": str(healing_path), "mode": "suggest_only"})

    next_actions = [
        "Đọc codenomad-plan.md trước khi cho phép chạy lệnh thật.",
        "Chạy lại với --execute chỉ khi các command đã an toàn.",
        "Nếu có lỗi, xem codenomad-healing-plan.md và sửa nguyên nhân gốc.",
    ]
    report = RuntimeReport(task, str(plan_path), str(context_path), results, healing_attempts, passed, next_actions, utc_now())
    report_path = root / "docs/runtime/codenomad-runtime-report.md"
    report_path.write_text(report.to_markdown(), encoding="utf-8")
    append_session_memory(root, {"task": task, "dry_run": dry_run, "passed": passed, "report": str(report_path), "plan": str(plan_path)})
    return report


def export_json_report(report: RuntimeReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
