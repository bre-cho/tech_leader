from __future__ import annotations

import json
from typing import Any
from sqlalchemy.orm import Session
from app.models.records import WorkflowRunRecord

REQUIRED_LINEAGE_FIELDS = ["artifact_id", "source_task_id", "agent_id", "input_hash", "checksum", "status"]


class ArtifactAuditor:
    def __init__(self, db: Session):
        self.db = db

    def run(self) -> dict[str, Any]:
        runs = self.db.query(WorkflowRunRecord).all()
        total = len(runs)
        missing_lineage = []
        complete = 0

        for run in runs:
            artifact = self._extract_artifact(run)
            if artifact is None:
                missing_lineage.append({"workflow_id": run.workflow_id, "missing": "artifact_not_found"})
                continue
            missing_fields = [f for f in REQUIRED_LINEAGE_FIELDS if not artifact.get(f)]
            if missing_fields:
                missing_lineage.append({"workflow_id": run.workflow_id, "missing_fields": missing_fields})
            else:
                complete += 1

        status = "PASS" if not missing_lineage else "WARN" if complete > 0 else "FAIL"

        return {
            "artifact_lineage_status": status,
            "total_workflow_runs": total,
            "complete_lineage": complete,
            "missing_lineage": missing_lineage[:20],
            "required_fields": REQUIRED_LINEAGE_FIELDS,
        }

    def _extract_artifact(self, run: WorkflowRunRecord) -> dict | None:
        try:
            output = json.loads(run.output_json or "{}")
            return output.get("artifact")
        except Exception:
            return None
