from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from . import design_agents as agents
from .contracts import AgentEnvelope


class TechnicalLeadRuntime:
    """Closed-loop orchestrator. Replace persistence calls with your repository services."""

    def __init__(self) -> None:
        self.events: List[AgentEnvelope] = []

    def _record(self, envelope: AgentEnvelope) -> Dict[str, Any]:
        self.events.append(envelope)
        return envelope.output

    def run_phase1(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = payload.get("project_id") or str(uuid4())
        business = self._record(agents.business_diagnosis(project_id, payload))
        industry = self._record(agents.industry_adaptation(project_id, payload))
        image = self._record(agents.image_design(project_id, {**payload, **business, **industry}))
        scored = []
        for concept in image["concepts"]:
            score = self._record(agents.image_qa(project_id, concept))
            scored.append({**concept, **score})
        return {"project_id": project_id, "business": business, "industry": industry, "image_variants": scored}

    def run_after_image_selected(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = payload["project_id"]
        upsell = self._record(agents.upsell_opportunity(project_id, payload))
        concept = self._record(agents.video_concept(project_id, {**payload, **upsell}))
        story = self._record(agents.storyboard(project_id, {**payload, **concept}))
        offer = self._record(agents.offer(project_id, {**payload, **story}))
        return {"project_id": project_id, "upsell": upsell, "video_concept": concept, "storyboard": story, "offer": offer}

    def audit_snapshot(self) -> Dict[str, Any]:
        return {
            "agent_run_count": len(self.events),
            "steps": [e.lineage.step for e in self.events],
            "warnings": [w for e in self.events for w in e.warnings],
            "go_no_go": "GO" if len(self.events) > 0 and not any(e.confidence_score < 60 for e in self.events) else "NO-GO",
        }
