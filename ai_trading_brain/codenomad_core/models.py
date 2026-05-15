from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

RiskLevel = Literal["low", "medium", "high", "blocked"]
CommandStatus = Literal["pending", "approved", "denied", "executed", "failed", "skipped"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ProjectFile:
    path: str
    kind: str
    size_bytes: int
    lines: int
    risk_flags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectContext:
    repo_root: str
    generated_at: str
    files: list[ProjectFile]
    languages: dict[str, int]
    docs_present: list[str]
    tests_present: list[str]
    scripts_present: list[str]
    package_managers: list[str]
    risk_summary: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ExecutionStep:
    id: str
    title: str
    intent: str
    commands: list[str]
    files_to_touch: list[str]
    risk: RiskLevel
    validation: list[str]
    rollback: list[str]
    requires_approval: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ExecutionPlan:
    task: str
    created_at: str
    repo_root: str
    goal: str
    assumptions: list[str]
    steps: list[ExecutionStep]
    manual_test: list[str]
    approval_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# CodeNomad Execution Plan",
            "",
            f"- Created at: `{self.created_at}`",
            f"- Task: {self.task}",
            f"- Goal: {self.goal}",
            f"- Approval required: `{self.approval_required}`",
            "",
            "## Assumptions",
        ]
        lines += [f"- {item}" for item in self.assumptions] or ["- None"]
        lines.append("")
        lines.append("## Steps")
        for step in self.steps:
            lines += [
                f"### {step.id}. {step.title}",
                f"- Intent: {step.intent}",
                f"- Risk: `{step.risk}`",
                f"- Requires approval: `{step.requires_approval}`",
                "- Commands:",
            ]
            lines += [f"  - `{cmd}`" for cmd in step.commands] or ["  - None"]
            lines.append("- Files to touch:")
            lines += [f"  - `{p}`" for p in step.files_to_touch] or ["  - None"]
            lines.append("- Validation:")
            lines += [f"  - {v}" for v in step.validation] or ["  - None"]
            lines.append("- Rollback:")
            lines += [f"  - {r}" for r in step.rollback] or ["  - None"]
            lines.append("")
        lines.append("## Manual Test")
        lines += [f"- {item}" for item in self.manual_test] or ["- None"]
        return "\n".join(lines).strip() + "\n"


@dataclass(slots=True)
class CommandResult:
    command: str
    status: CommandStatus
    return_code: int | None
    stdout: str
    stderr: str
    started_at: str
    finished_at: str
    duration_ms: int
    risk: RiskLevel
    healing_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RuntimeReport:
    task: str
    plan_path: str
    context_path: str
    results: list[CommandResult]
    self_healing_attempts: list[dict[str, Any]]
    passed: bool
    next_actions: list[str]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# CodeNomad Runtime Report",
            "",
            f"- Created at: `{self.created_at}`",
            f"- Task: {self.task}",
            f"- Passed: `{self.passed}`",
            f"- Plan: `{self.plan_path}`",
            f"- Context: `{self.context_path}`",
            "",
            "## Command Results",
        ]
        for result in self.results:
            lines += [
                f"### `{result.command}`",
                f"- Status: `{result.status}`",
                f"- Return code: `{result.return_code}`",
                f"- Duration: `{result.duration_ms}ms`",
                f"- Risk: `{result.risk}`",
            ]
            if result.healing_hint:
                lines.append(f"- Healing hint: {result.healing_hint}")
            if result.stdout:
                lines += ["", "Stdout:", "```", result.stdout[-2000:], "```"]
            if result.stderr:
                lines += ["", "Stderr:", "```", result.stderr[-2000:], "```"]
            lines.append("")
        lines.append("## Self Healing Attempts")
        if self.self_healing_attempts:
            for attempt in self.self_healing_attempts:
                lines.append(f"- {attempt}")
        else:
            lines.append("- None")
        lines.append("")
        lines.append("## Next Actions")
        lines += [f"- {item}" for item in self.next_actions] or ["- None"]
        return "\n".join(lines).strip() + "\n"
