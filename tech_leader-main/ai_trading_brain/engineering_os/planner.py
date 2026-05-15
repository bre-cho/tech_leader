from __future__ import annotations

from pathlib import Path
from .context_graph import build_context_graph
from .models import PhasePlan, PlanStep
from .skills import load_skills, recommend_skills

HIGH_RISK_KEYWORDS = ["migration", "database", "payment", "auth", "security", "delete", "production", "deploy"]


def _candidate_files(task: str, repo_root: Path) -> list[str]:
    graph = build_context_graph(repo_root)
    words = {w.strip(".,:;()[]{}-_/").lower() for w in task.split() if len(w) > 3}
    candidates: list[str] = []
    for node in graph.nodes:
        haystack = f"{node.path} {' '.join(node.tags)} {' '.join(node.exports)}".lower()
        if any(word in haystack for word in words):
            candidates.append(node.path)
    essentials = ["AGENTS.md", "docs/master-plan.md", "CHANGELOG.md"]
    for item in essentials:
        if (repo_root / item).exists() and item not in candidates:
            candidates.insert(0, item)
    return candidates[:20]


def create_phase_plan(task: str, repo_root: str | Path = ".") -> PhasePlan:
    root = Path(repo_root).resolve()
    skills = recommend_skills(task, load_skills(root))
    files = _candidate_files(task, root)
    task_lower = task.lower()
    high_risk = any(keyword in task_lower for keyword in HIGH_RISK_KEYWORDS)
    migration_impact = "Requires explicit reversible migration plan" if "migration" in task_lower or "database" in task_lower else "No schema migration detected from task text"
    steps = [
        PlanStep(
            id="1",
            title="Read constitution and project memory",
            owner_agent="Planner Agent",
            files=["AGENTS.md", "docs/brief.md", "docs/BRD.md", "docs/master-plan.md"],
            actions=["Load project constraints", "Identify acceptance criteria", "Confirm architecture boundaries"],
            verification=["Context files exist or are generated", "Task is mapped to explicit goal"],
            risk="low",
        ),
        PlanStep(
            id="2",
            title="Build engineering context graph",
            owner_agent="Context Graph Agent",
            files=files[:10],
            actions=["Scan modules, tests, docs, workflows", "Detect dependency impact", "Export runtime graph JSON"],
            verification=["context-graph.json generated", "High-risk files listed"],
            risk="medium" if files else "low",
        ),
        PlanStep(
            id="3",
            title="Implement additive patch only",
            owner_agent="Builder Agent",
            files=files,
            actions=["Apply smallest safe change", "Avoid unrelated refactors", "Preserve public contracts"],
            verification=["No unrelated files changed", "New/changed behavior has tests"],
            risk="high" if high_risk else "medium",
        ),
        PlanStep(
            id="4",
            title="Run verification gate",
            owner_agent="QA Agent",
            files=["tests/", "docs/runtime/verification-report.md"],
            actions=["Run py_compile", "Run pytest", "Run configured smoke tests", "Capture outputs"],
            verification=["All required checks pass or report blockers"],
            risk="medium",
        ),
        PlanStep(
            id="5",
            title="Report and update organizational memory",
            owner_agent="Memory Agent",
            files=["CHANGELOG.md", "docs/changelogs/", "docs/runtime/engineering-memory.jsonl"],
            actions=["Write changelog", "Write verification report", "Append memory event"],
            verification=["Memory event contains task, decision, checks, rollback"],
            risk="low",
        ),
    ]
    return PhasePlan(
        task=task,
        goal=f"Deliver a governed, verified engineering change for: {task}",
        selected_skills=[skill.name for skill in skills],
        files_to_modify=files,
        dependency_impact=["Context graph must be rebuilt before code changes", "Tests touching modified modules must be run"],
        migration_impact=migration_impact,
        rollback_plan=["Keep patch additive where possible", "Revert changed files from VCS if verification fails", "For migrations, include down migration before approval"],
        manual_verification=["Review generated phase plan", "Inspect changed files", "Run smoke command from report", "Approve release gate before deploy"],
        steps=steps,
        risks=["Context drift if docs are stale", "Architecture drift if unrelated refactor occurs"] + (["High-risk production/schema/security operation requires approval"] if high_risk else []),
        approval_required=high_risk,
    )
