from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from . import design_agents as agents
from .contracts import AgentEnvelope


class TechnicalLeadRuntime:
    """Closed-loop orchestrator. Replace persistence calls with your repository services."""

    def __init__(self) -> None:
        self.events: List[AgentEnvelope] = []
        self.last_artifact_id: str | None = None

    def _record(self, envelope: AgentEnvelope) -> Dict[str, Any]:
        if not envelope.project_id:
            raise ValueError("project_id is required")
        if not envelope.trace_id:
            raise ValueError("trace_id is required")
        if envelope.lineage.parent_step_id is None and self.last_artifact_id is not None:
            envelope.lineage.parent_step_id = self.last_artifact_id
        self.events.append(envelope)
        self.last_artifact_id = envelope.lineage.output_artifact_id or envelope.lineage.artifact_id
        return envelope.output

    def run_phase1(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = payload.get("project_id") or str(uuid4())
        trace_id = payload.get("trace_id") or str(uuid4())
        business = self._record(agents.business_diagnosis(project_id, trace_id, payload))
        industry = self._record(agents.industry_adaptation(project_id, trace_id, payload))
        image = self._record(agents.image_design(project_id, trace_id, {**payload, **business, **industry}))
        scored = []
        for concept in image["concepts"]:
            score = self._record(agents.image_qa(project_id, trace_id, concept))
            scored.append({**concept, **score})
        return {
            "project_id": project_id,
            "trace_id": trace_id,
            "business": business,
            "industry": industry,
            "image_variants": scored,
        }

    def run_after_image_selected(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = payload.get("project_id")
        trace_id = payload.get("trace_id")
        if not project_id:
            raise ValueError("project_id is required")
        if not trace_id:
            raise ValueError("trace_id is required")

        upsell = self._record(agents.upsell_opportunity(project_id, trace_id, payload))
        concept = self._record(agents.video_concept(project_id, trace_id, {**payload, **upsell}))
        story = self._record(agents.storyboard(project_id, trace_id, {**payload, **concept}))
        offer = self._record(agents.offer(project_id, trace_id, {**payload, **story}))
        followup = self._record(agents.crm_followup(project_id, trace_id, {**payload, **offer}))
        analytics = self._record(agents.analytics_update(project_id, trace_id, {**payload, **upsell, **offer}))
        memory = self._record(agents.memory_update(project_id, trace_id, payload))
        audit = self._record(agents.techlead_audit(project_id, trace_id, payload))

        return {
            "project_id": project_id,
            "trace_id": trace_id,
            "upsell": upsell,
            "video_concept": concept,
            "storyboard": story,
            "offer": offer,
            "crm_followup": followup,
            "analytics": analytics,
            "memory": memory,
            "audit": audit,
        }

    def audit_snapshot(self) -> Dict[str, Any]:
        return {
            "agent_run_count": len(self.events),
            "trace_id": self.events[-1].trace_id if self.events else None,
            "project_id": self.events[-1].project_id if self.events else None,
            "steps": [e.lineage.step for e in self.events],
            "warnings": [w for e in self.events for w in e.warnings],
            "go_no_go": "GO" if len(self.events) > 0 and not any(e.confidence_score < 60 for e in self.events) else "NO-GO",
        }
