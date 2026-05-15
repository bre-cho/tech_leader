from __future__ import annotations

from pathlib import Path
import json

from ai_trading_brain.engineering_os import (
    build_context_graph,
    create_phase_plan,
    evaluate_phase_plan,
    run_engineering_os,
)


def test_context_graph_detects_python_modules(tmp_path: Path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.py").write_text("import json\n\ndef hello():\n    return json.dumps({})\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("from pkg.a import hello\n\ndef test_hello(): assert hello()\n", encoding="utf-8")
    graph = build_context_graph(tmp_path)
    assert graph.stats["total_nodes"] >= 2
    assert any(n.kind == "test" for n in graph.nodes)


def test_phase_plan_contains_governed_loop(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# constitution", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "master-plan.md").write_text("# plan", encoding="utf-8")
    plan = create_phase_plan("build backend api with smoke test", tmp_path)
    assert "backend-api.skill" in plan.selected_skills
    assert any(step.owner_agent == "QA Agent" for step in plan.steps)
    assert "Rollback Plan" in plan.to_markdown()


def test_governance_blocks_destructive_task(tmp_path: Path):
    plan = create_phase_plan("delete production secret and drop table", tmp_path)
    decision = evaluate_phase_plan(plan)
    assert decision.status == "blocked"
    assert decision.risk_level == "critical"


def test_runtime_writes_operational_artifacts(tmp_path: Path):
    (tmp_path / "sample.py").write_text("def ok(): return True\n", encoding="utf-8")
    result = run_engineering_os("create production review gate", tmp_path, verify=False)
    assert Path(result["phase_plan"]).exists()
    assert Path(result["context_graph"]).exists()
    assert (tmp_path / "docs/runtime/governance-decision.json").exists()
    data = json.loads((tmp_path / "docs/runtime/governance-decision.json").read_text(encoding="utf-8"))
    assert data["status"] in {"approved", "needs_human_approval", "blocked"}
