from __future__ import annotations

import json
from pathlib import Path
from .context_graph import build_context_graph
from .governance import evaluate_phase_plan
from .memory import append_memory_event
from .planner import create_phase_plan
from .verification import run_verification


def ensure_engineering_docs(repo_root: str | Path) -> None:
    root = Path(repo_root)
    dirs = [
        "docs/architecture", "docs/workflows", "docs/runtime", "docs/governance", "docs/playbooks",
        "docs/postmortems", "docs/decisions", "docs/changelogs", "skills",
    ]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)
    defaults = {
        "AGENTS.md": "# AGENTS.md — AI Governance Constitution\n\n- Always propose a plan before execution.\n- Preserve architecture consistency.\n- Prefer additive patches.\n- Validate before deploy.\n- Every feature must include a smoke test.\n- Schema-breaking changes require human approval and rollback.\n- Always update CHANGELOG.md and docs/runtime reports.\n",
        "docs/brief.md": "# Project Brief\n\nThis file stores high-level intent for AI agents.\n",
        "docs/BRD.md": "# Business Requirements Document\n\n## Users\n## Pain Points\n## Core Flows\n## Constraints\n## Priorities\n",
        "docs/master-plan.md": "# Master Plan\n\n## Phase 1 — Foundation\n- [ ] Maintain project constitution\n- [ ] Build context graph\n- [ ] Enforce verification gate\n",
        "CHANGELOG.md": "# Changelog\n",
    }
    for rel, content in defaults.items():
        path = root / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")


def run_engineering_os(task: str, repo_root: str | Path = ".", verify: bool = True) -> dict[str, object]:
    root = Path(repo_root).resolve()
    ensure_engineering_docs(root)
    graph = build_context_graph(root)
    graph_path = graph.write_json(root / "docs/runtime/context-graph.json")
    plan = create_phase_plan(task, root)
    plan_path = root / "docs/runtime/phase-plan.md"
    plan_path.write_text(plan.to_markdown(), encoding="utf-8")
    decision = evaluate_phase_plan(plan)
    decision_path = root / "docs/runtime/governance-decision.json"
    decision_path.write_text(json.dumps(decision.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    report_path = None
    report_passed = None
    if verify:
        report = run_verification(task, root)
        report_path = root / "docs/runtime/verification-report.md"
        report_path.write_text(report.to_markdown(), encoding="utf-8")
        report_passed = report.passed
    memory_path = append_memory_event(root, {
        "task": task,
        "plan_path": str(plan_path.relative_to(root)),
        "governance": decision.to_dict(),
        "context_graph_path": str(graph_path.relative_to(root)),
        "verification_passed": report_passed,
    })
    return {
        "task": task,
        "context_graph": str(graph_path),
        "phase_plan": str(plan_path),
        "governance_decision": decision.to_dict(),
        "verification_report": str(report_path) if report_path else None,
        "memory": str(memory_path),
    }
