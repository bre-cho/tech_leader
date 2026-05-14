from __future__ import annotations

import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.records import StatePropagationRecord


class StatePropagationTracker:
    """
    Records every state handoff between agents during a workflow run.

    Call record() after each _run_agent() step to build a complete
    cross-agent state propagation graph for audit and gap analysis.
    """

    def __init__(self, db: Session, workflow_id: str):
        self.db = db
        self.workflow_id = workflow_id

    def record(
        self,
        source_agent: str,
        target_agent: str,
        state_key: str,
        value=None,
    ) -> None:
        row = StatePropagationRecord(
            workflow_id=self.workflow_id,
            source_agent=source_agent,
            target_agent=target_agent,
            state_key=state_key,
            value_json=json.dumps(value, ensure_ascii=False, default=str) if value is not None else None,
        )
        self.db.add(row)
        self.db.commit()

    def get_transitions(self) -> list[dict]:
        rows = (
            self.db.query(StatePropagationRecord)
            .filter(StatePropagationRecord.workflow_id == self.workflow_id)
            .order_by(StatePropagationRecord.created_at)
            .all()
        )
        return [
            {
                "source_agent": r.source_agent,
                "target_agent": r.target_agent,
                "state_key": r.state_key,
                "created_at": str(r.created_at),
            }
            for r in rows
        ]

    def detect_missing_transitions(self, expected_sequence: list[str]) -> list[str]:
        """
        Given an ordered list of agent names that should have propagated state,
        return names of agents that never appear as source_agent in the log.
        """
        rows = (
            self.db.query(StatePropagationRecord.source_agent)
            .filter(StatePropagationRecord.workflow_id == self.workflow_id)
            .distinct()
            .all()
        )
        recorded = {r.source_agent for r in rows}
        return [a for a in expected_sequence if a not in recorded]
