from __future__ import annotations

import json
from pathlib import Path
from .models import SkillDefinition

DEFAULT_SKILLS = [
    SkillDefinition(
        name="backend-api.skill",
        trigger_keywords=["api", "route", "endpoint", "backend", "service"],
        description="Create/update backend API with validation, service layer, tests, docs and smoke command.",
        required_checks=["py_compile", "pytest", "api_contract"],
        file_patterns=["**/*route*", "**/*service*", "tests/**"],
    ),
    SkillDefinition(
        name="production-review.skill",
        trigger_keywords=["security", "performance", "review", "deploy", "production"],
        description="Run production review across security, performance, observability and deployment readiness.",
        required_checks=["py_compile", "pytest", "security_scan", "smoke"],
        file_patterns=["docs/**", ".github/workflows/**"],
    ),
    SkillDefinition(
        name="context-graph.skill",
        trigger_keywords=["context", "graph", "dependency", "architecture", "module"],
        description="Build engineering context graph and detect module/dependency impact.",
        required_checks=["context_graph", "orphan_scan"],
        file_patterns=["**/*.py", "docs/architecture/**"],
    ),
    SkillDefinition(
        name="release-gate.skill",
        trigger_keywords=["release", "gate", "approval", "rollback", "migration"],
        description="Evaluate release risk, approval requirements, rollback and verification contract.",
        required_checks=["governance_gate", "rollback_plan", "pytest"],
        file_patterns=["docs/governance/**", "**/migrations/**"],
    ),
]


def load_skills(repo_root: str | Path) -> list[SkillDefinition]:
    root = Path(repo_root)
    skills = list(DEFAULT_SKILLS)
    for path in (root / "skills").glob("*.json") if (root / "skills").exists() else []:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            skills.append(SkillDefinition(**data))
        except Exception:
            continue
    return skills


def recommend_skills(task: str, skills: list[SkillDefinition]) -> list[SkillDefinition]:
    lowered = task.lower()
    scored: list[tuple[int, SkillDefinition]] = []
    for skill in skills:
        score = sum(1 for keyword in skill.trigger_keywords if keyword in lowered)
        if score:
            scored.append((score, skill))
    if not scored:
        return [s for s in skills if s.name in {"context-graph.skill", "release-gate.skill"}]
    return [skill for _, skill in sorted(scored, key=lambda item: item[0], reverse=True)[:3]]
