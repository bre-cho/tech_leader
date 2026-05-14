from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session
from app.models.records import ReplaySnapshotRecord


class ReplayAuditor:
    def __init__(self, db: Session):
        self.db = db

    def run(self) -> dict[str, Any]:
        snapshots = self.db.query(ReplaySnapshotRecord).all()
        total = len(snapshots)

        missing_manifests = []
        drift_violations = []
        no_input_hash = []

        for s in snapshots:
            has_manifest = bool(s.input_hash) and bool(s.runtime_version)
            if not has_manifest:
                missing_manifests.append({"snapshot_id": s.snapshot_id, "workflow_id": s.workflow_id})
            if not s.input_hash:
                no_input_hash.append(s.snapshot_id)

        status = "PASS" if not missing_manifests else "WARN"

        return {
            "replay_status": status,
            "total_snapshots": total,
            "missing_manifests": missing_manifests[:20],
            "snapshots_without_input_hash": no_input_hash[:20],
            "drift_violations": drift_violations,
        }
