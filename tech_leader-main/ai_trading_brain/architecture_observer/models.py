from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Literal
import json

RiskLevel = Literal["low", "medium", "high", "critical"]

@dataclass(frozen=True)
class FileNode:
    path: str
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    size_bytes: int = 0

@dataclass(frozen=True)
class ChangeSet:
    changed_files: list[str]
    before_graph_path: str | None = None
    after_graph_path: str | None = None
    summary: str = ""

@dataclass(frozen=True)
class BlastRadiusReport:
    changed_files: list[str]
    directly_impacted: list[str]
    indirectly_impacted: list[str]
    risk_level: RiskLevel
    recommendations: list[str]

@dataclass(frozen=True)
class DriftReport:
    drift_score: float
    violations: list[str]
    risk_level: RiskLevel
    recommendations: list[str]

@dataclass(frozen=True)
class DependencyEvolutionSnapshot:
    nodes: list[FileNode]
    edges: list[dict[str, Any]]
    changed_since_last: list[str]
    hotspots: list[str]

@dataclass(frozen=True)
class ArchitectureObserverReport:
    blast_radius: BlastRadiusReport
    drift: DriftReport
    dependency_evolution: DependencyEvolutionSnapshot

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write_json(self, path: str | Path) -> Path:
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return out
