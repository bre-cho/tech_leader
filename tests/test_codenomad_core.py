from __future__ import annotations

from pathlib import Path

from ai_trading_brain.codenomad_core import create_codenomad_plan, run_codenomad_runtime, run_command, scan_project_context
from ai_trading_brain.codenomad_core.healing import build_healing_plan
from ai_trading_brain.codenomad_core.safety import classify_command


def test_context_scan_detects_python_files(tmp_path: Path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "demo.py").write_text("print('ok')\n", encoding="utf-8")
    ctx = scan_project_context(tmp_path)
    assert ctx.languages.get(".py") == 1
    assert any(f.path == "scripts/demo.py" for f in ctx.files)


def test_safety_blocks_destructive_command():
    risk = classify_command("rm -rf /")
    assert risk.level == "blocked"
    assert risk.requires_approval is True


def test_safe_command_dry_run():
    result = run_command("python -V", dry_run=True)
    assert result.status == "skipped"
    assert result.return_code is None
    assert "DRY RUN" in result.stdout


def test_plan_contains_validation_and_rollback(tmp_path: Path):
    (tmp_path / "tests").mkdir()
    plan = create_codenomad_plan("fix failing tests", tmp_path)
    text = plan.to_markdown()
    assert "Rollback" in text
    assert "Manual Test" in text
    assert plan.steps


def test_runtime_writes_reports(tmp_path: Path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "demo.py").write_text("print('ok')\n", encoding="utf-8")
    report = run_codenomad_runtime("audit project", tmp_path, dry_run=True)
    assert report.passed is True
    assert (tmp_path / "docs/runtime/codenomad-plan.md").exists()
    assert (tmp_path / "docs/runtime/codenomad-runtime-report.md").exists()
    assert (tmp_path / ".codenomad_core/sessions.jsonl").exists()


def test_healing_plan_from_missing_module_log(tmp_path: Path):
    report = tmp_path / "report.md"
    report.write_text("ModuleNotFoundError: No module named 'x'", encoding="utf-8")
    plan = build_healing_plan(report)
    assert "dependency" in plan.lower() or "import" in plan.lower()
