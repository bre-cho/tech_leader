from __future__ import annotations

import logging

try:
    from prometheus_client import Counter
except ImportError:  # pragma: no cover
    Counter = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# =========================
# Canonical states
# =========================
RENDER_JOB_STATES = {
    "queued",
    "dispatching",
    "polling",
    "merging",
    "burning_subtitles",
    "completed",
    "failed",
    "queue_error",
    "identity_review",         # Avatar identity check failed post-render; pending reject/requeue
    "identity_review_error",   # QA infrastructure exception; requires manual operator review
    "identity_gate_failed",    # Render failed IDENTITY_GATE_THRESHOLD; queued for re-render
    "re_render_queued",        # Re-render triggered after identity gate failure
    "quality_remediation",     # Render quality below PUBLISH_QUALITY_THRESHOLD; hint injected
}

RENDER_SCENE_STATES = {
    "queued",
    "submitted",
    "processing",
    "succeeded",
    "failed",
    "canceled",
}


# =========================
# Transition maps
# =========================
RENDER_JOB_TRANSITIONS: dict[str, set[str]] = {
    "queued": {"dispatching", "failed", "queue_error"},
    "dispatching": {"polling", "failed", "queue_error"},
    "polling": {"merging", "burning_subtitles", "completed", "failed", "identity_review"},
    "merging": {"burning_subtitles", "completed", "failed", "identity_review"},
    "burning_subtitles": {"completed", "failed", "identity_review"},
    "queue_error": {"failed"},
    "identity_review": {"queued", "completed", "failed", "identity_gate_failed", "quality_remediation", "identity_review_error"},
    "identity_review_error": {"identity_review", "queued", "failed"},  # retry review or fail
    "identity_gate_failed": {"re_render_queued", "failed"},  # re-render or hard fail
    "re_render_queued": {"queued", "failed"},  # fed back into the render pipeline
    "quality_remediation": {"queued", "completed", "failed"},  # re-queue or accept/fail
    "completed": set(),
    "failed": set(),
}

RENDER_SCENE_TRANSITIONS: dict[str, set[str]] = {
    "queued": {"submitted", "failed"},
    "submitted": {"processing", "succeeded", "failed", "canceled"},
    "processing": {"processing", "succeeded", "failed", "canceled"},
    "succeeded": set(),
    "failed": {"queued"},   # allow scene-level remediation requeue
    "canceled": {"queued"}, # allow requeue of canceled scenes
}


# =========================
# Metrics
# =========================
# States for which a self-transition (same → same) is explicitly allowed.
# ``render_scene_task`` allows processing→processing as a polling-refresh
# heartbeat.  All other same-state transitions are rejected so that bugs
# that accidentally call assert_valid_transition with an unchanged state do
# not silently pass.
_SAME_STATE_ALLOWED: dict[str, set[str]] = {
    "render_scene_task": {"processing"},
}


if Counter is not None:
    _TRANSITION_COUNTER = Counter(
        "render_fsm_transition_attempts_total",
        "Render FSM transition attempts partitioned by entity type and result.",
        ("entity_type", "result"),
    )
else:  # pragma: no cover
    _TRANSITION_COUNTER = None

_METRIC_SNAPSHOT: dict[str, int] = {
    "job_invalid_transition_attempts": 0,
    "scene_invalid_transition_attempts": 0,
    "job_valid_transition_attempts": 0,
    "scene_valid_transition_attempts": 0,
}


def _increment_metric(*, entity_type: str, result: str) -> None:
    if entity_type == "render_job":
        key = "job_valid_transition_attempts" if result == "valid" else "job_invalid_transition_attempts"
    else:
        key = "scene_valid_transition_attempts" if result == "valid" else "scene_invalid_transition_attempts"
    _METRIC_SNAPSHOT[key] += 1
    if _TRANSITION_COUNTER is not None:
        _TRANSITION_COUNTER.labels(entity_type=entity_type, result=result).inc()


# =========================
# Exceptions
# =========================
class InvalidTransitionError(ValueError):
    pass


# =========================
# Helpers
# =========================
def _normalize_state(value: str) -> str:
    return value.strip().lower()


def _allowed_targets(
    *,
    entity_type: str,
    current_state: str,
) -> set[str]:
    if entity_type == "render_job":
        return RENDER_JOB_TRANSITIONS.get(current_state, set())
    if entity_type == "render_scene_task":
        return RENDER_SCENE_TRANSITIONS.get(current_state, set())
    raise ValueError(f"Unknown entity_type: {entity_type}")


def _known_states(entity_type: str) -> set[str]:
    if entity_type == "render_job":
        return RENDER_JOB_STATES
    if entity_type == "render_scene_task":
        return RENDER_SCENE_STATES
    raise ValueError(f"Unknown entity_type: {entity_type}")


def can_transition(
    *,
    entity_type: str,
    current_state: str,
    next_state: str,
) -> bool:
    current_state = _normalize_state(current_state)
    next_state = _normalize_state(next_state)

    known = _known_states(entity_type)
    if current_state not in known or next_state not in known:
        return False

    if current_state == next_state:
        # Allow only explicitly whitelisted self-transitions (e.g. scene
        # processing→processing for polling refresh).  All other same-state
        # calls are rejected to surface bugs early.
        return next_state in _SAME_STATE_ALLOWED.get(entity_type, set())

    return next_state in _allowed_targets(entity_type=entity_type, current_state=current_state)


def assert_valid_transition(
    *,
    entity_type: str,
    entity_id: str,
    current_state: str,
    next_state: str,
    context: dict | None = None,
) -> None:
    current_state = _normalize_state(current_state)
    next_state = _normalize_state(next_state)
    context = context or {}

    if can_transition(
        entity_type=entity_type,
        current_state=current_state,
        next_state=next_state,
    ):
        _increment_metric(entity_type=entity_type, result="valid")
        if entity_type == "render_job":
            logger.debug(
                "METRIC render_fsm_job_transition entity_id=%s %s->%s",
                entity_id, current_state, next_state,
            )
        else:
            logger.debug(
                "METRIC render_fsm_scene_transition entity_id=%s %s->%s",
                entity_id, current_state, next_state,
            )
        return

    allowed = sorted(_allowed_targets(entity_type=entity_type, current_state=current_state))

    _increment_metric(entity_type=entity_type, result="invalid")

    logger.error(
        "METRIC render_fsm_invalid_transition entity_type=%s entity_id=%s current_state=%s next_state=%s allowed_targets=%s context=%s",
        entity_type,
        entity_id,
        current_state,
        next_state,
        allowed,
        context,
    )

    raise InvalidTransitionError(
        f"Invalid transition for {entity_type} {entity_id}: {current_state} -> {next_state}. Allowed: {allowed}"
    )


def get_transition_metrics_snapshot() -> dict[str, int]:
    return dict(_METRIC_SNAPSHOT)


def describe_fsm() -> dict[str, dict[str, list[str]]]:
    return {
        "render_jobs": {state: sorted(list(targets)) for state, targets in RENDER_JOB_TRANSITIONS.items()},
        "render_scene_tasks": {state: sorted(list(targets)) for state, targets in RENDER_SCENE_TRANSITIONS.items()},
    }
