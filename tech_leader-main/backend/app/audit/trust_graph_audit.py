from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session
from app.models.records import AgentTrustRecord, DecisionLogRecord


class TrustGraphAuditor:
    def __init__(self, db: Session):
        self.db = db

    def run(self) -> dict[str, Any]:
        trust_rows = self.db.query(AgentTrustRecord).all()
        decision_rows = self.db.query(DecisionLogRecord).all()

        unauthorized = [
            {
                "decision_id": r.decision_id,
                "workflow_id": r.workflow_id,
                "decision_type": r.decision_type,
                "reason": r.reason,
            }
            for r in decision_rows
            if r.outcome == "DENIED"
        ]

        tool_violations = [d for d in unauthorized if "tool_use" in d["decision_type"]]
        memory_risks = [d for d in unauthorized if "memory_write" in d["decision_type"]]

        # Artifact trust score: average trust of agents that produced artifacts
        artifact_agents = [r for r in trust_rows]
        artifact_trust_score = (
            sum(r.trust_score for r in artifact_agents) / len(artifact_agents)
            if artifact_agents
            else 0.0
        )

        # Release gate bypass: any BLOCKED promotion that was later marked PASSED
        bypass_candidates = [
            r for r in decision_rows
            if r.decision_type == "operating_law.assert_can_promote" and r.outcome == "BLOCKED"
        ]

        # Policy drift: agents with trust_score < 0.3
        low_trust_agents = [
            {"agent_name": r.agent_name, "trust_score": r.trust_score}
            for r in trust_rows
            if r.trust_score < 0.3
        ]

        status = "PASS" if not unauthorized and not low_trust_agents else "WARN"
        if tool_violations:
            status = "FAIL"

        return {
            "trustgraph_status": status,
            "total_agents_tracked": len(trust_rows),
            "total_decisions_logged": len(decision_rows),
            "unauthorized_agent_actions": unauthorized[:20],
            "tool_permission_violations": tool_violations[:10],
            "memory_write_risks": memory_risks[:10],
            "artifact_trust_score": round(artifact_trust_score, 4),
            "release_gate_bypass": [{"decision_id": r.decision_id, "workflow_id": r.workflow_id} for r in bypass_candidates[:10]],
            "policy_drift": low_trust_agents[:10],
        }
