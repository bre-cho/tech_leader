from __future__ import annotations

import hashlib
import json
from sqlalchemy.orm import Session
from app.models.records import RetryStateRecord

MAX_RETRIES = 3


class RetryGuard:
    """
    Idempotency guard for agent retries.

    Computes a stable idempotency_key from (workflow_id + agent_name + input_hash)
    and prevents re-execution beyond MAX_RETRIES.
    """

    def __init__(self, db: Session):
        self.db = db

    def _key(self, workflow_id: str, agent_name: str, input_payload: str) -> str:
        raw = f"{workflow_id}:{agent_name}:{input_payload}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def check_and_record(
        self,
        workflow_id: str,
        agent_name: str,
        input_payload: str,
    ) -> dict:
        """
        Returns {"allowed": bool, "attempt_count": int, "idempotency_key": str}.
        Raises RuntimeError if the agent has exceeded MAX_RETRIES.
        """
        key = self._key(workflow_id, agent_name, input_payload)
        row = self.db.query(RetryStateRecord).filter(RetryStateRecord.idempotency_key == key).first()

        if row is None:
            row = RetryStateRecord(
                idempotency_key=key,
                workflow_id=workflow_id,
                agent_name=agent_name,
                attempt_count=1,
                last_status="running",
            )
            self.db.add(row)
            self.db.commit()
            return {"allowed": True, "attempt_count": 1, "idempotency_key": key}

        if row.attempt_count >= MAX_RETRIES:
            return {
                "allowed": False,
                "attempt_count": row.attempt_count,
                "idempotency_key": key,
                "reason": f"max_retries ({MAX_RETRIES}) exceeded",
            }

        row.attempt_count += 1
        row.last_status = "running"
        self.db.commit()
        return {"allowed": True, "attempt_count": row.attempt_count, "idempotency_key": key}

    def mark_success(self, workflow_id: str, agent_name: str, input_payload: str) -> None:
        key = self._key(workflow_id, agent_name, input_payload)
        row = self.db.query(RetryStateRecord).filter(RetryStateRecord.idempotency_key == key).first()
        if row:
            row.last_status = "succeeded"
            self.db.commit()

    def mark_failed(self, workflow_id: str, agent_name: str, input_payload: str) -> None:
        key = self._key(workflow_id, agent_name, input_payload)
        row = self.db.query(RetryStateRecord).filter(RetryStateRecord.idempotency_key == key).first()
        if row:
            row.last_status = "failed"
            self.db.commit()
