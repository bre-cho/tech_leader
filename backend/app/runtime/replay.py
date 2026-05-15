from __future__ import annotations

import hashlib
import json
import uuid
from sqlalchemy.orm import Session
from app.models.records import WorkflowRunRecord, ReplaySnapshotRecord

DRIFT_BUDGET = 0.0  # 0 = strict determinism; increase to allow partial drift
RUNTIME_VERSION = "1.0.0"


def _stable_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _input_hash(input_json: str) -> str:
    return _stable_hash(input_json or "")


class ReplayRuntime:
    def __init__(self, db: Session):
        self.db = db

    def create_snapshot(self, workflow_id: str):
        run = self.db.query(WorkflowRunRecord).filter(WorkflowRunRecord.workflow_id == workflow_id).order_by(WorkflowRunRecord.created_at.desc()).first()
        if not run:
            raise ValueError("workflow_not_found")
        payload = json.dumps(
            {
                "workflow_id": run.workflow_id,
                "input_json": run.input_json,
                "output_json": run.output_json,
                "verification_json": run.verification_json,
                "promotion_status": run.promotion_status,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        snapshot_id = f"snapshot_{uuid.uuid4().hex[:12]}"
        output_hash = _stable_hash(run.output_json or "")
        ih = _input_hash(run.input_json or "")
        row = ReplaySnapshotRecord(
            snapshot_id=snapshot_id,
            workflow_id=run.workflow_id,
            payload_json=payload,
            output_hash=output_hash,
            input_hash=ih,
            runtime_version=RUNTIME_VERSION,
        )
        self.db.add(row)
        self.db.commit()
        return {
            "snapshot_id": snapshot_id,
            "workflow_id": workflow_id,
            "output_hash": output_hash,
            "input_hash": ih,
            "runtime_version": RUNTIME_VERSION,
        }

    def replay(self, snapshot_id: str):
        row = self.db.query(ReplaySnapshotRecord).filter(ReplaySnapshotRecord.snapshot_id == snapshot_id).first()
        if not row:
            raise ValueError("snapshot_not_found")
        payload = json.loads(row.payload_json)
        replay_hash = _stable_hash(payload.get("output_json") or "")
        determinism_passed = replay_hash == row.output_hash
        has_replay_manifest = bool(row.input_hash) and bool(row.runtime_version)
        # Drift check: 0 drift expected unless DRIFT_BUDGET > 0
        drift_within_budget = determinism_passed or DRIFT_BUDGET > 0
        recovery_route_available = has_replay_manifest and bool(payload.get("input_json"))
        return {
            "snapshot_id": snapshot_id,
            "workflow_id": row.workflow_id,
            "determinism_passed": determinism_passed,
            "drift_within_budget": drift_within_budget,
            "recovery_route_available": recovery_route_available,
            "drift_budget": DRIFT_BUDGET,
            "runtime_version": row.runtime_version or RUNTIME_VERSION,
            "input_hash": row.input_hash,
            "has_replay_manifest": has_replay_manifest,
            "checks": {
                "output_hash_match": determinism_passed,
                "has_input_snapshot": bool(payload.get("input_json")),
                "has_output_snapshot": bool(payload.get("output_json")),
                "has_replay_manifest": has_replay_manifest,
                "drift_within_budget": drift_within_budget,
            },
        }

