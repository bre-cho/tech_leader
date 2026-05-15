from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session
from app.models.records import DecisionLogRecord


class DecisionLogger:
    """Persist every governance decision to the database."""

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        workflow_id: str,
        decision_type: str,
        outcome: str,
        reason: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        import json

        decision_id = "dec_" + uuid.uuid4().hex[:12]
        row = DecisionLogRecord(
            decision_id=decision_id,
            workflow_id=workflow_id,
            decision_type=decision_type,
            outcome=outcome,
            reason=reason,
            metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
        )
        self.db.add(row)
        self.db.commit()
        return decision_id

    def query_by_workflow(self, workflow_id: str) -> list[dict[str, Any]]:
        import json

        rows = (
            self.db.query(DecisionLogRecord)
            .filter(DecisionLogRecord.workflow_id == workflow_id)
            .order_by(DecisionLogRecord.created_at)
            .all()
        )
        return [
            {
                "decision_id": r.decision_id,
                "workflow_id": r.workflow_id,
                "decision_type": r.decision_type,
                "outcome": r.outcome,
                "reason": r.reason,
                "metadata": json.loads(r.metadata_json or "{}"),
                "created_at": str(r.created_at),
            }
            for r in rows
        ]

    def query_denied(self, limit: int = 100) -> list[dict[str, Any]]:
        import json

        rows = (
            self.db.query(DecisionLogRecord)
            .filter(DecisionLogRecord.outcome == "DENIED")
            .order_by(DecisionLogRecord.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "decision_id": r.decision_id,
                "workflow_id": r.workflow_id,
                "decision_type": r.decision_type,
                "reason": r.reason,
                "metadata": json.loads(r.metadata_json or "{}"),
                "created_at": str(r.created_at),
            }
            for r in rows
        ]
