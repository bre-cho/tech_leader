"""
Job Contract
============
Python mirror of lib/contracts/job-contract.ts.

Canonical type definitions and lifecycle states for asynchronous jobs in the
AI ads generation pipeline.

Governance:
- All job state transitions MUST follow the canonical lifecycle defined here.
- New job types MUST be registered in JOB_TYPE_REGISTRY before use.
- Breaking changes to job payloads require a schema version bump.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ─── Job lifecycle ────────────────────────────────────────────────────────────


class JobStatus(str, Enum):
    """Canonical job status values.

    pending  → queued  → running  → completed
                       ↓           ↓
                     failed      failed
    """

    pending = "pending"
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


# ─── Job types ────────────────────────────────────────────────────────────────


class JobType(str, Enum):
    image_generation = "image_generation"
    ad_campaign = "ad_campaign"
    poster_production = "poster_production"
    poster_to_video = "poster_to_video"
    winner_learning = "winner_learning"
    retrain = "retrain"


@dataclass(frozen=True)
class JobTypeRegistryEntry:
    type: JobType
    name: str
    entry_route: str
    timeout_ms: int
    supports_idempotency: bool
    result_persisted: bool
    description: str


JOB_TYPE_REGISTRY: list[JobTypeRegistryEntry] = [
    JobTypeRegistryEntry(
        type=JobType.image_generation,
        name="Image Generation",
        entry_route="/api/jobs",
        timeout_ms=30_000,
        supports_idempotency=True,
        result_persisted=True,
        description=(
            "Generates images via DALL-E based on a prompt. Runs in the background "
            "using next/server after(). Results are uploaded to Supabase storage."
        ),
    ),
    JobTypeRegistryEntry(
        type=JobType.ad_campaign,
        name="Ad Campaign Generation",
        entry_route="/api/v6/generate",
        timeout_ms=30_000,
        supports_idempotency=False,
        result_persisted=False,
        description=(
            "Generates a full multi-variant ad campaign using the V6Pro engine, including "
            "scoring, winner selection, and industry routing."
        ),
    ),
    JobTypeRegistryEntry(
        type=JobType.poster_production,
        name="Poster Production Pipeline",
        entry_route="/api/poster-production/run",
        timeout_ms=60_000,
        supports_idempotency=False,
        result_persisted=True,
        description=(
            "Six-stage poster production pipeline: CIG graph → industry routing → V6Pro → "
            "V4Poster → QA → autofix. Trace written to configured backend."
        ),
    ),
    JobTypeRegistryEntry(
        type=JobType.poster_to_video,
        name="Poster-to-Video Conversion",
        entry_route="/api/poster-intelligence/poster-to-video",
        timeout_ms=30_000,
        supports_idempotency=False,
        result_persisted=False,
        description=(
            "Converts a poster design to a video plan using the configured video provider. "
            "Provider 'mock' is blocked in production-like runtimes."
        ),
    ),
    JobTypeRegistryEntry(
        type=JobType.winner_learning,
        name="Winner Learning",
        entry_route="/api/scale-intelligence/learn-winner",
        timeout_ms=10_000,
        supports_idempotency=True,
        result_persisted=True,
        description=(
            "Processes a CTR learning event and updates the winner DNA registry. "
            "Restricted to internal signed ingest callers."
        ),
    ),
    JobTypeRegistryEntry(
        type=JobType.retrain,
        name="Model Retrain",
        entry_route="/api/self-learning-ai/retrain",
        timeout_ms=120_000,
        supports_idempotency=False,
        result_persisted=False,
        description="Triggers a model retrain cycle. Restricted to internal ops callers.",
    ),
]

# ─── Job record ───────────────────────────────────────────────────────────────


@dataclass
class JobRecord:
    id: str
    user_id: str
    type: JobType
    status: JobStatus
    input: dict[str, Any]
    result: dict[str, Any] | None
    error: str | None
    idempotency_key: str | None
    created_at: str
    updated_at: str
    started_at: str | None
    completed_at: str | None


# ─── Helpers ──────────────────────────────────────────────────────────────────


def get_job_type_definition(job_type: JobType) -> JobTypeRegistryEntry | None:
    """Returns the registry entry for the given job type, or None."""
    return next((e for e in JOB_TYPE_REGISTRY if e.type == job_type), None)


def get_idempotent_job_types() -> list[JobTypeRegistryEntry]:
    """Returns all job types that support idempotency-key deduplication."""
    return [e for e in JOB_TYPE_REGISTRY if e.supports_idempotency]


def is_terminal_status(status: JobStatus) -> bool:
    """Returns True when the status represents a terminal state."""
    return status in (JobStatus.completed, JobStatus.failed, JobStatus.cancelled)
