from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

class CodeNode(BaseModel):
    id: str
    path: str
    module: str
    kind: Literal["python", "typescript", "javascript", "config", "doc", "test", "unknown"]
    layer: str
    size_bytes: int
    lines: int
    imports: list[str] = Field(default_factory=list)
    exports: list[str] = Field(default_factory=list)
    functions: list[str] = Field(default_factory=list)
    classes: list[str] = Field(default_factory=list)
    risk_tags: list[str] = Field(default_factory=list)

class CodeEdge(BaseModel):
    source: str
    target: str
    relation: Literal["imports", "references", "owns", "runtime_depends"]
    weight: float = 1.0
    evidence: str = ""

class CodeGraphSnapshot(BaseModel):
    snapshot_id: str
    repo_root: str
    created_at: str
    nodes: list[CodeNode]
    edges: list[CodeEdge]
    modules: dict[str, list[str]]
    summary: dict[str, Any]

class BlastRadiusReport(BaseModel):
    changed_files: list[str]
    touched_modules: list[str]
    impacted_nodes: list[str]
    impacted_edges: list[CodeEdge]
    blast_radius_score: int
    risk_level: Literal["low", "medium", "high", "critical"]
    reasons: list[str]

class DriftReport(BaseModel):
    passed: bool
    drift_score: int
    violations: list[str]
    warnings: list[str]
    layer_drift: dict[str, Any]
    dependency_drift: dict[str, Any]

class PromotionDecision(BaseModel):
    status: Literal["promote", "block", "manual_review"]
    score: int
    required_score: int = 85
    reasons: list[str]
    blast_radius: BlastRadiusReport
    drift: DriftReport

class ArchitectureRunReport(BaseModel):
    status: Literal["ready", "blocked", "manual_review"]
    before_snapshot: CodeGraphSnapshot | None = None
    after_snapshot: CodeGraphSnapshot
    blast_radius_report: BlastRadiusReport | None = None
    drift_report: DriftReport | None = None
    promotion_decision: PromotionDecision | None = None
    artifacts: list[str] = Field(default_factory=list)
