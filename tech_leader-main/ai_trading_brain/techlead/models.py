from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

Severity = Literal["P0", "P1", "P2", "P3", "INFO"]
Phase = Literal[
    "PHASE_1_INVENTORY_RUNTIME_GRAPH_DETECTION",
    "PHASE_2_STATIC_SYSTEM_SCAN",
    "PHASE_3_RUNTIME_VALIDATION",
    "PHASE_4_ARCHITECTURE_AUDIT",
    "PHASE_5_PATCH_PLANNING",
    "PHASE_6_SAFE_AUTOFIX",
]

class ReleaseGate(str, Enum):
    GO = "GO"
    REVIEW = "REVIEW"
    NO_GO = "NO-GO"

@dataclass(frozen=True)
class Finding:
    severity: Severity
    phase: Phase
    category: str
    path: str
    message: str
    recommendation: str
    evidence: dict[str, Any] = field(default_factory=dict)

    @property
    def is_blocking(self) -> bool:
        return self.severity in {"P0", "P1"}

@dataclass(frozen=True)
class AgentContract:
    name: str
    role: str
    required_inputs: list[str]
    produced_outputs: list[str]
    blocks_without: list[str] = field(default_factory=list)
    live_trading_sensitive: bool = False

@dataclass
class AuditReport:
    repo_root: str
    release_gate: ReleaseGate
    executive_summary: str
    findings: list[Finding]
    graph: dict[str, Any]
    runtime_results: dict[str, Any]
    patch_plan: list[Finding]
    fixed: list[Finding] = field(default_factory=list)
    direct_commands: dict[str, list[str]] = field(default_factory=dict)
    business_operating: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["release_gate"] = self.release_gate.value
        return data

    def write_json(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        import json
        p.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def to_markdown(self) -> str:
        def render(title: str, items: list[Finding]) -> str:
            lines = [f"## {title}", ""]
            if not items:
                lines.append("✅ Không có mục trong nhóm này.")
                return "\n".join(lines) + "\n"
            for i, f in enumerate(items, 1):
                lines.append(f"{i}. **{f.severity} / {f.category}** — `{f.path}`")
                lines.append(f"   - Vấn đề: {f.message}")
                lines.append(f"   - Hướng sửa: {f.recommendation}")
                if f.evidence:
                    compact = {k: v for k, v in f.evidence.items() if v not in (None, "", [], {})}
                    if compact:
                        lines.append(f"   - Evidence: `{compact}`")
            return "\n".join(lines) + "\n"

        p0 = [f for f in self.findings if f.severity == "P0"]
        p1 = [f for f in self.findings if f.severity == "P1"]
        graph = [f for f in self.findings if "graph" in f.category.lower()]
        memory = [f for f in self.findings if "memory" in f.category.lower()]
        runtime = [f for f in self.findings if f.phase == "PHASE_3_RUNTIME_VALIDATION"]
        security = [f for f in self.findings if "secret" in f.category.lower() or "security" in f.category.lower()]
        lines = [
            "# Agent 16 — TrustGraph Context Graph Audit Report",
            "",
            f"**Repo:** `{self.repo_root}`",
            f"**Release Gate:** **{self.release_gate.value}**",
            "",
            "## Executive Summary",
            self.executive_summary,
            "",
            render("Blocking Errors P0", p0),
            render("High Risk P1", p1),
            render("Graph Integrity Report", graph),
            render("Memory Consistency Audit", memory),
            render("Runtime / CI Validation", runtime),
            render("Security Drift", security),
            render("File-by-file Patch Plan", self.patch_plan),
            "## Business Operating Mind",
            "",
            f"Business OS State: `{self.business_operating.get('release_gate', 'not_run')}`",
            f"Business OS Top Opportunity: `{(self.business_operating.get('opportunities') or [{}])[0].get('title', 'none')}`",
            "",
            render("Safe Auto-fixes Applied", self.fixed),
            "## Direct Commands for Claude Code / Cursor / Copilot",
            "",
        ]
        for tool, cmds in self.direct_commands.items():
            lines.append(f"### {tool}")
            lines.append("```bash")
            lines.extend(cmds)
            lines.append("```")
        return "\n".join(lines)

    def write_markdown(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.to_markdown(), encoding="utf-8")
