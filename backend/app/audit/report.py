from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel


class ExecutiveSummary(BaseModel):
    release_gate_status: str  # GO | NO-GO
    blocking_error_count: int
    warning_count: int
    modules_audited: List[str]
    overall_health_score: float  # 0.0 – 1.0


class GraphIntegrityReport(BaseModel):
    context_graph_status: str
    trust_graph_status: str
    missing_nodes: List[str]
    broken_edges: List[Any]
    cyclic_dependencies: List[Any]
    unauthorized_actions: List[Any]
    policy_drift: List[Any]


class WorkforceRiskMatrix(BaseModel):
    workforce_status: str
    total_agents: int
    agents_with_gaps: List[Any]
    required_contracts: List[str]


class OrchestrationGapAnalysis(BaseModel):
    replay_status: str
    artifact_lineage_status: str
    missing_manifests: List[Any]
    missing_lineage: List[Any]


class MemoryConsistencyAudit(BaseModel):
    memory_topology_status: str
    org_memory_status: str
    missing_memory_layers: List[str]
    stale_memory: List[Any]
    conflicting_decisions: List[Any]


class ReleaseGateDecision(BaseModel):
    status: str  # GO | NO-GO
    reason: str
    blocking_failures: List[str]


class SystemAuditReport(BaseModel):
    executive_summary: ExecutiveSummary
    graph_integrity: GraphIntegrityReport
    workforce_risk: WorkforceRiskMatrix
    orchestration_gaps: OrchestrationGapAnalysis
    memory_consistency: MemoryConsistencyAudit
    release_gate: ReleaseGateDecision
    raw: dict[str, Any] = {}
