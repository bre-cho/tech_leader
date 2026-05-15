from __future__ import annotations

from pathlib import Path

from ai_trading_brain.techlead import Agent16Config, TechnicalLeadAgent
from ai_trading_brain.techlead.graph_builder import ContextGraphBuilder


def test_agent16_builds_report_without_runtime(tmp_path: Path) -> None:
    (tmp_path / "ai_trading_brain").mkdir()
    (tmp_path / "ai_trading_brain" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "ai_trading_brain" / "brain_runtime.py").write_text("class X:\n    pass\n", encoding="utf-8")
    report = TechnicalLeadAgent(tmp_path, Agent16Config(runtime=False, apply_safe_fixes=True)).run()
    assert report.release_gate.value in {"GO", "REVIEW", "NO-GO"}
    assert (tmp_path / "context_graph" / "entities.jsonl").exists()


def test_context_graph_detects_python_entities(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "mod.py").write_text("import os\nclass A: pass\ndef f(): return 1\n", encoding="utf-8")
    graph = ContextGraphBuilder(tmp_path).build()
    ids = {x["id"] for x in graph["entities"]}
    assert "class:pkg.mod.A" in ids
    assert "function:pkg.mod.f" in ids


def test_business_operating_mind_generates_runtime_report(tmp_path: Path) -> None:
    pkg = tmp_path / "ai_trading_brain"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "execution_runtime.py").write_text("def run():\n    return 'ok'\n", encoding="utf-8")
    from ai_trading_brain.techlead.business_operating import BusinessOperatingMind

    report = BusinessOperatingMind(tmp_path).run([], {"summary": {"entities": 2, "edges": 1}})
    assert report.opportunities
    assert report.context_graph["summary"]["entities"] > 0
    assert report.adaptive_deployment["decision"] in {"BLOCK_DEPLOYMENT", "REVIEW_BEFORE_DEPLOYMENT", "ALLOW_CONTROLLED_PROMOTION"}


def test_agent16_embeds_business_operating_output(tmp_path: Path) -> None:
    (tmp_path / "ai_trading_brain").mkdir()
    (tmp_path / "ai_trading_brain" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "ai_trading_brain" / "brain_runtime.py").write_text("class Runtime:\n    pass\n", encoding="utf-8")
    report = TechnicalLeadAgent(tmp_path, Agent16Config(runtime=False, apply_safe_fixes=False, business_operating_mind=True)).run()
    assert report.business_operating
    assert (tmp_path / ".agent16-business-os" / "business_operating_report.json").exists()
