from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Literal
import json

NodeKind = Literal["module", "script", "test", "doc", "workflow", "config", "skill", "unknown"]
RiskLevel = Literal["low", "medium", "high", "critical"]
DecisionStatus = Literal["approved", "needs_human_approval", "blocked"]


@dataclass(frozen=True)
class EngineeringNode:
    id: str
    path: str
    kind: NodeKind
    language: str
    size_bytes: int
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EngineeringEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0


@dataclass
class ContextGraph:
    repo_root: str
    nodes: list[EngineeringNode] = field(default_factory=list)
    edges: list[EngineeringEdge] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write_json(self, path: str | Path) -> Path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return out


@dataclass
class PlanStep:
    id: str
    title: str
    owner_agent: str
    files: list[str]
    actions: list[str]
    verification: list[str]
    risk: RiskLevel = "low"


@dataclass
class PhasePlan:
    task: str
    goal: str
    selected_skills: list[str]
    files_to_modify: list[str]
    dependency_impact: list[str]
    migration_impact: str
    rollback_plan: list[str]
    manual_verification: list[str]
    steps: list[PlanStep]
    risks: list[str]
    approval_required: bool

    def to_markdown(self) -> str:
        lines = [
            f"# Phase Plan — {self.task}",
            "",
            "## Goal",
            self.goal,
            "",
            "## Selected Skills",
            *([f"- {skill}" for skill in self.selected_skills] or ["- none"]),
            "",
            "## Files to Modify",
            *([f"- `{file}`" for file in self.files_to_modify] or ["- none"]),
            "",
            "## Dependency Impact",
            *([f"- {item}" for item in self.dependency_impact] or ["- none"]),
            "",
            "## Migration Impact",
            self.migration_impact,
            "",
            "## Risks",
            *([f"- {risk}" for risk in self.risks] or ["- none"]),
            "",
            "## Rollback Plan",
            *([f"- {item}" for item in self.rollback_plan] or ["- restore previous commit"]),
            "",
            "## Execution Steps",
        ]
        for step in self.steps:
            lines.extend([
                f"### {step.id}. {step.title}",
                f"- Owner: {step.owner_agent}",
                f"- Risk: {step.risk}",
                "- Files:",
                *([f"  - `{f}`" for f in step.files] or ["  - none"]),
                "- Actions:",
                *[f"  - {a}" for a in step.actions],
                "- Verification:",
                *[f"  - {v}" for v in step.verification],
                "",
            ])
        lines.extend(["## Manual Verification", *[f"- {item}" for item in self.manual_verification]])
        return "\n".join(lines).strip() + "\n"


@dataclass
class GovernanceDecision:
    status: DecisionStatus
    risk_level: RiskLevel
    reasons: list[str]
    required_approvals: list[str]
    blocked_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VerificationCheck:
    name: str
    command: str
    passed: bool
    output: str


@dataclass
class VerificationReport:
    task: str
    passed: bool
    checks: list[VerificationCheck]
    recommendations: list[str]

    def to_markdown(self) -> str:
        lines = [f"# Verification Report — {self.task}", "", f"Overall: {'PASS' if self.passed else 'FAIL'}", "", "## Checks"]
        for check in self.checks:
            lines.extend([
                f"### {'✅' if check.passed else '❌'} {check.name}",
                f"Command: `{check.command}`",
                "```text",
                check.output[-4000:],
                "```",
                "",
            ])
        lines.extend(["## Recommendations", *([f"- {item}" for item in self.recommendations] or ["- none"])])
        return "\n".join(lines).strip() + "\n"


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    trigger_keywords: list[str]
    description: str
    required_checks: list[str]
    file_patterns: list[str]
