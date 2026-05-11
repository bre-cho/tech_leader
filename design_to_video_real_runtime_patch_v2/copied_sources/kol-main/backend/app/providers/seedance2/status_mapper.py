from __future__ import annotations

from typing import Any

TERMINAL_SUCCESS = {"succeeded", "success", "completed", "done"}
TERMINAL_FAILURE = {"failed", "error", "cancelled", "canceled", "timeout"}
RUNNING = {"queued", "pending", "running", "processing", "submitted"}


def normalize_seedance2_status(raw: dict[str, Any]) -> dict[str, Any]:
    status_raw = str(raw.get("status") or raw.get("state") or "unknown").lower()
    if status_raw in TERMINAL_SUCCESS:
        status = "succeeded"
    elif status_raw in TERMINAL_FAILURE:
        status = "failed"
    elif status_raw in RUNNING:
        status = "running"
    else:
        status = "unknown"

    output_url = raw.get("output_url") or raw.get("video_url") or raw.get("url")
    error = raw.get("error") or raw.get("message") if status == "failed" else None
    return {
        "status": status,
        "provider_status": status_raw,
        "output_url": output_url,
        "error": error,
        "raw": raw,
    }
