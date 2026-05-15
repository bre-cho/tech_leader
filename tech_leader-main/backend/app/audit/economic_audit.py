from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session
from app.models.records import WorkflowRunRecord
from app.cognition.strategic_mapper import StrategicObjectiveMapper
from app.cognition.economic_memory import EconomicMemoryStore

import json


class EconomicCognitionAuditor:
    def __init__(self, db: Session, economic_store: EconomicMemoryStore | None = None):
        self.db = db
        self._mapper = StrategicObjectiveMapper()
        self._econ = economic_store or EconomicMemoryStore()

    def run(self) -> dict[str, Any]:
        runs = self.db.query(WorkflowRunRecord).all()

        business_objectives_detected = []
        unmapped_tasks = []

        for run in runs:
            try:
                inp = json.loads(run.input_json or "{}")
                industry = inp.get("industry", "")
                if not industry:
                    unmapped_tasks.append({"workflow_id": run.workflow_id, "reason": "no_industry_field"})
                    continue
                if self._mapper.is_mapped(industry):
                    mapping = self._mapper.map(industry)
                    business_objectives_detected.append({
                        "workflow_id": run.workflow_id,
                        "industry": industry,
                        "goal": mapping["mapped_business_goal"],
                        "revenue_impact": mapping["revenue_impact"],
                    })
                else:
                    unmapped_tasks.append({"workflow_id": run.workflow_id, "industry": industry, "reason": "industry_not_in_map"})
            except Exception:
                unmapped_tasks.append({"workflow_id": run.workflow_id, "reason": "parse_error"})

        growth_loops = self._econ.get_growth_loops()
        revenue_intelligence = self._econ.get_revenue_intelligence()

        missing_revenue_flow = not revenue_intelligence
        missing_growth_loop = not growth_loops

        strategic_blindspots = []
        if missing_revenue_flow:
            strategic_blindspots.append("No revenue intelligence records found in economic memory")
        if missing_growth_loop:
            strategic_blindspots.append("No growth loop patterns recorded")
        if unmapped_tasks:
            strategic_blindspots.append(f"{len(unmapped_tasks)} task(s) not mapped to any business objective")

        status = "PASS" if not strategic_blindspots else "WARN"

        return {
            "economic_cognition_status": status,
            "business_objectives_detected": business_objectives_detected[:10],
            "unmapped_tasks": unmapped_tasks[:10],
            "growth_loops_recorded": len(growth_loops),
            "revenue_intelligence_records": len(revenue_intelligence),
            "missing_revenue_flow": missing_revenue_flow,
            "missing_growth_loop": missing_growth_loop,
            "strategic_blindspots": strategic_blindspots,
        }
