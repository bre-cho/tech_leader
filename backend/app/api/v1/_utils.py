from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from fastapi import HTTPException


def require_project_and_trace(payload: Dict[str, Any]) -> tuple[str, str]:
    project_id = payload.get("project_id")
    trace_id = payload.get("trace_id")
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id is required")
    if not trace_id:
        raise HTTPException(status_code=400, detail="trace_id is required")
    return str(project_id), str(trace_id)


def standard_response(
    project_id: str,
    trace_id: str,
    data: Dict[str, Any],
    step: str,
    warnings: list[str] | None = None,
    parent_step_id: str | None = None,
    artifact_id: str | None = None,
) -> Dict[str, Any]:
    return {
        "ok": True,
        "trace_id": trace_id,
        "project_id": project_id,
        "data": data,
        "warnings": warnings or [],
        "lineage": {
            "step": step,
            "parent_step_id": parent_step_id,
            "artifact_id": artifact_id or str(uuid4()),
        },
    }
