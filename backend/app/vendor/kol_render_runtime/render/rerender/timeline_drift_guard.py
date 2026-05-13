from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TimelineDriftResult:
    ok: bool
    duration_delta_ms: int
    threshold_ms: int
    reason: str


def validate_timeline_drift(
    *,
    old_duration_sec: float | int | None,
    new_duration_sec: float | int | None,
    threshold_ms: int | None = None,
) -> TimelineDriftResult:
    threshold = threshold_ms or int(os.getenv("RERENDER_TIMELINE_DRIFT_THRESHOLD_MS", "250"))
    if old_duration_sec is None or new_duration_sec is None:
        return TimelineDriftResult(ok=True, duration_delta_ms=0, threshold_ms=threshold, reason="duration_unknown")
    delta = abs(int(float(new_duration_sec) * 1000) - int(float(old_duration_sec) * 1000))
    if delta <= threshold:
        return TimelineDriftResult(ok=True, duration_delta_ms=delta, threshold_ms=threshold, reason="within_budget")
    return TimelineDriftResult(ok=False, duration_delta_ms=delta, threshold_ms=threshold, reason="duration_drift_exceeded")
