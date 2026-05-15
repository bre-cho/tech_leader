from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from app.audit.context_graph_audit import ContextGraphAuditor
from app.audit.trust_graph_audit import TrustGraphAuditor
from app.audit.memory_audit import MemoryAuditor
from app.audit.artifact_audit import ArtifactAuditor
from app.audit.workforce_audit import WorkforceAuditor
from app.audit.replay_audit import ReplayAuditor
from app.audit.org_memory_audit import OrgMemoryAuditor
from app.audit.report import (
    SystemAuditReport,
    ExecutiveSummary,
    GraphIntegrityReport,
    WorkforceRiskMatrix,
    OrchestrationGapAnalysis,
    MemoryConsistencyAudit,
    ReleaseGateDecision,
)

_PASS_STATUSES = {"PASS", "GO"}
_FAIL_STATUSES = {"FAIL", "NO-GO"}


class AuditOrchestrator:
    def __init__(self, db: Session):
        self.db = db

    def run(self) -> SystemAuditReport:
        context_graph = ContextGraphAuditor(self.db).run()
        trust_graph = TrustGraphAuditor(self.db).run()
        memory = MemoryAuditor().run()
        artifact = ArtifactAuditor(self.db).run()
        workforce = WorkforceAuditor().run()
        replay = ReplayAuditor(self.db).run()
        org_memory = OrgMemoryAuditor(self.db).run()

        raw = {
            "context_graph": context_graph,
            "trust_graph": trust_graph,
            "memory": memory,
            "artifact": artifact,
            "workforce": workforce,
            "replay": replay,
            "org_memory": org_memory,
        }

        # Blocking failures = any FAIL status
        blocking = []
        warnings = []
        for module_name, result in raw.items():
            status_key = next((k for k in result if k.endswith("_status")), None)
            status = result.get(status_key, "UNKNOWN") if status_key else "UNKNOWN"
            if status in _FAIL_STATUSES:
                blocking.append(f"{module_name}: {status}")
            elif status not in _PASS_STATUSES:
                warnings.append(f"{module_name}: {status}")

        gate_status = "GO" if not blocking else "NO-GO"
        total_modules = len(raw)
        passing = total_modules - len(blocking) - len(warnings)
        health_score = round(passing / total_modules, 4) if total_modules else 0.0

        executive = ExecutiveSummary(
            release_gate_status=gate_status,
            blocking_error_count=len(blocking),
            warning_count=len(warnings),
            modules_audited=list(raw.keys()),
            overall_health_score=health_score,
        )

        graph_integrity = GraphIntegrityReport(
            context_graph_status=context_graph["context_graph_status"],
            trust_graph_status=trust_graph["trustgraph_status"],
            missing_nodes=context_graph["missing_nodes"],
            broken_edges=context_graph["broken_edges"],
            cyclic_dependencies=context_graph["cyclic_dependencies"],
            unauthorized_actions=trust_graph["unauthorized_agent_actions"],
            policy_drift=trust_graph["policy_drift"],
        )

        workforce_risk = WorkforceRiskMatrix(
            workforce_status=workforce["workforce_status"],
            total_agents=workforce["total_agents"],
            agents_with_gaps=workforce["agents_with_gaps"],
            required_contracts=workforce["required_contracts"],
        )

        orchestration_gaps = OrchestrationGapAnalysis(
            replay_status=replay["replay_status"],
            artifact_lineage_status=artifact["artifact_lineage_status"],
            missing_manifests=replay["missing_manifests"],
            missing_lineage=artifact["missing_lineage"],
        )

        memory_consistency = MemoryConsistencyAudit(
            memory_topology_status=memory["memory_topology_status"],
            org_memory_status=org_memory["org_memory_status"],
            missing_memory_layers=memory["missing_memory_layers"],
            stale_memory=memory["stale_memory"],
            conflicting_decisions=org_memory["conflicting_decisions"],
        )

        release_gate = ReleaseGateDecision(
            status=gate_status,
            reason="All audit modules passed" if gate_status == "GO" else f"Blocking failures: {blocking}",
            blocking_failures=blocking,
        )

        return SystemAuditReport(
            executive_summary=executive,
            graph_integrity=graph_integrity,
            workforce_risk=workforce_risk,
            orchestration_gaps=orchestration_gaps,
            memory_consistency=memory_consistency,
            release_gate=release_gate,
            raw=raw,
        )
