"""
Replay Contract
===============
Python mirror of lib/contracts/replay-contract.ts.

Canonical type definitions for deterministic replay of pipeline runs.
A replay re-executes a prior job from a saved snapshot, producing an output
that must be bitwise-equivalent to the original within allowed tolerances.

Governance:
- Every replay MUST reference a valid, persisted job snapshot.
- Replay outputs MUST be validated by the determinism gate before acceptance.
- Non-deterministic providers (e.g. live AI models) MUST be stubbed or frozen
  when replaying; only mock/deterministic provider variants are permitted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ─── Replay status ────────────────────────────────────────────────────────────


class ReplayStatus(str, Enum):
    pending = "pending"
    loading = "loading"
    running = "running"
    validating = "validating"
    passed = "passed"
    failed = "failed"
    cancelled = "cancelled"


# ─── Determinism gate ─────────────────────────────────────────────────────────


class DeterminismCheckId(str, Enum):
    artifact_checksum = "artifact_checksum"
    score_tolerance = "score_tolerance"
    provider_frozen = "provider_frozen"
    trace_structure = "trace_structure"


@dataclass
class DeterminismGateCheck:
    check_id: DeterminismCheckId
    passed: bool
    detail: str
    delta: float | None
    tolerance: float | None


# ─── Replay snapshot ──────────────────────────────────────────────────────────


@dataclass
class ReplayTraceEntry:
    stage: str
    duration_ms: int
    provider: str
    artifact_checksum: str | None


@dataclass
class ReplaySnapshot:
    snapshot_id: str
    source_job_id: str
    frozen_input: dict[str, Any]
    artifact_checksums: dict[str, str]
    original_trace: list[ReplayTraceEntry]
    captured_at: str
    schema_version: str


# ─── Replay record ────────────────────────────────────────────────────────────


@dataclass
class ReplayRecord:
    id: str
    snapshot_id: str
    user_id: str
    status: ReplayStatus
    gate_checks: list[DeterminismGateCheck]
    determinism_passed: bool | None
    created_at: str
    completed_at: str | None
    error: str | None


# ─── Registry ─────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DeterminismCheckRegistryEntry:
    check_id: DeterminismCheckId
    name: str
    required: bool
    tolerance: float | None
    description: str


DETERMINISM_CHECK_REGISTRY: list[DeterminismCheckRegistryEntry] = [
    DeterminismCheckRegistryEntry(
        check_id=DeterminismCheckId.artifact_checksum,
        name="Artifact Checksum",
        required=True,
        tolerance=None,
        description=(
            "SHA-256 checksum of every artifact produced in the replay MUST exactly match "
            "the checksum recorded in the original snapshot. Any divergence is a hard failure."
        ),
    ),
    DeterminismCheckRegistryEntry(
        check_id=DeterminismCheckId.score_tolerance,
        name="Score Tolerance",
        required=True,
        tolerance=0.01,
        description=(
            "Quality scores (attention, trust, conversion, visual, total) must be within "
            "±1 % of the original run values. Larger divergence indicates non-deterministic "
            "scoring."
        ),
    ),
    DeterminismCheckRegistryEntry(
        check_id=DeterminismCheckId.provider_frozen,
        name="Provider Frozen",
        required=True,
        tolerance=None,
        description=(
            "No live provider calls may be made during replay. All provider invocations "
            "must be intercepted and served from frozen deterministic fixtures."
        ),
    ),
    DeterminismCheckRegistryEntry(
        check_id=DeterminismCheckId.trace_structure,
        name="Trace Structure",
        required=True,
        tolerance=None,
        description=(
            "The sequence of pipeline stages executed during replay must be identical to "
            "the original run. Stage additions, removals, or reorderings are a hard failure."
        ),
    ),
]

# ─── Helpers ──────────────────────────────────────────────────────────────────


def get_determinism_check_definition(
    check_id: DeterminismCheckId,
) -> DeterminismCheckRegistryEntry | None:
    """Returns the registry entry for the given check ID, or None."""
    return next((c for c in DETERMINISM_CHECK_REGISTRY if c.check_id == check_id), None)


def get_required_determinism_checks() -> list[DeterminismCheckRegistryEntry]:
    """Returns all required determinism checks."""
    return [c for c in DETERMINISM_CHECK_REGISTRY if c.required]


def is_determinism_gate_passed(checks: list[DeterminismGateCheck]) -> bool:
    """Returns True only when all required checks have passed."""
    required_ids = {c.check_id for c in DETERMINISM_CHECK_REGISTRY if c.required}
    check_map = {c.check_id: c for c in checks}
    return all(check_map.get(cid, DeterminismGateCheck(cid, False, "", None, None)).passed
               for cid in required_ids)
