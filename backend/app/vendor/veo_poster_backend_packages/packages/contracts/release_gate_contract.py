"""
Release Gate Contract
=====================
Python mirror of lib/contracts/release-gate-contract.ts.

Defines the canonical release gate checks that MUST all pass before any
deployment or publish operation is permitted. The gate enforces quality,
security, and operational readiness across the full stack.

Gate checks (in evaluation order):
  1. build          – TypeScript build must be clean (npm run build PASS)
  2. governance     – All governance tests must pass (npm run test:governance PASS)
  3. mock_leakage   – No mock leakage in production paths (npm run check:mock-leakage PASS)
  4. backend_tests  – Python backend tests must pass (pytest PASS)
  5. migrations     – Database schema is up-to-date (alembic upgrade head PASS)
  6. auth_policy    – All API routes have registered auth policy (auth-policy PASS)

Governance:
- ALL checks must pass; partial passes do not unblock deployment.
- Each check has a canonical ID; new checks must be registered here.
- Blocking a check requires an explicit rationale and a tracking issue.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

# ─── Gate check types ─────────────────────────────────────────────────────────


class GateCheckId(str, Enum):
    build = "build"
    governance = "governance"
    mock_leakage = "mock_leakage"
    backend_tests = "backend_tests"
    migrations = "migrations"
    auth_policy = "auth_policy"


class GateCheckStatus(str, Enum):
    pass_ = "pass"
    fail = "fail"
    skipped = "skipped"
    pending = "pending"


@dataclass
class GateCheckResult:
    check_id: GateCheckId
    status: GateCheckStatus
    completed_at: str | None
    duration_ms: int | None
    summary: str
    error: str | None
    skip_rationale: str | None


# ─── Gate check registry ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class GateCheckRegistryEntry:
    check_id: GateCheckId
    name: str
    command: str
    required: bool
    skippable: bool
    timeout_ms: int
    description: str


GATE_CHECK_REGISTRY: list[GateCheckRegistryEntry] = [
    GateCheckRegistryEntry(
        check_id=GateCheckId.build,
        name="TypeScript Build",
        command="npm run build",
        required=True,
        skippable=False,
        timeout_ms=300_000,
        description=(
            "Runs the full Next.js TypeScript build. Catches type errors, missing imports, "
            "and any compile-time regressions before code reaches production."
        ),
    ),
    GateCheckRegistryEntry(
        check_id=GateCheckId.governance,
        name="Governance Tests",
        command="npm run test:governance",
        required=True,
        skippable=False,
        timeout_ms=120_000,
        description=(
            "Runs the governance test suite: auth policy, contract versions, observability, "
            "runtime fallback, approval token rotation, write-route auth hardening, scoring "
            "regression, rate limit distributed, and render contract tests."
        ),
    ),
    GateCheckRegistryEntry(
        check_id=GateCheckId.mock_leakage,
        name="Mock Leakage Check",
        command="npm run check:mock-leakage",
        required=True,
        skippable=False,
        timeout_ms=30_000,
        description=(
            "Scans production code paths for forbidden mock provider references. "
            "Mock usage is only permitted in dev/test; leakage into production routes "
            "is a blocking error."
        ),
    ),
    GateCheckRegistryEntry(
        check_id=GateCheckId.backend_tests,
        name="Python Backend Tests",
        command="pytest -q",
        required=True,
        skippable=False,
        timeout_ms=120_000,
        description=(
            "Runs the full Python pytest suite for the poster-engine-backend service. "
            "Covers auth, provider adapters, scoring engine, export storage, and "
            "production hardening."
        ),
    ),
    GateCheckRegistryEntry(
        check_id=GateCheckId.migrations,
        name="Database Migrations",
        command="alembic upgrade head",
        required=True,
        skippable=False,
        timeout_ms=60_000,
        description=(
            "Applies all pending Alembic migrations to verify schema compatibility. "
            "Ensures the target database can be migrated to the head revision without errors."
        ),
    ),
    GateCheckRegistryEntry(
        check_id=GateCheckId.auth_policy,
        name="Auth Policy Registry",
        command="npm run test:auth-policy",
        required=True,
        skippable=False,
        timeout_ms=30_000,
        description=(
            "Validates that every app/api route method has a registered entry in "
            "AUTH_POLICY_REGISTRY. Prevents auth drift where new routes are accidentally "
            "left unauthenticated."
        ),
    ),
]

# ─── Gate result ──────────────────────────────────────────────────────────────


@dataclass
class ReleaseGateResult:
    approved: bool
    evaluated_at: str
    checks: list[GateCheckResult]
    blocked_by: list[GateCheckId]
    skipped: list[GateCheckId]


# ─── Helpers ──────────────────────────────────────────────────────────────────


def get_gate_check_definition(
    check_id: GateCheckId,
) -> GateCheckRegistryEntry | None:
    """Returns the registry entry for the given check ID, or None."""
    return next((c for c in GATE_CHECK_REGISTRY if c.check_id == check_id), None)


def get_required_gate_checks() -> list[GateCheckRegistryEntry]:
    """Returns all required gate checks."""
    return [c for c in GATE_CHECK_REGISTRY if c.required]


def evaluate_release_gate(checks: list[GateCheckResult]) -> ReleaseGateResult:
    """Evaluates a list of check results and returns a ReleaseGateResult.

    A gate is approved when every required, non-skipped check has status 'pass'.
    """
    blocked_by: list[GateCheckId] = []
    skipped: list[GateCheckId] = []

    for check in checks:
        if check.status == GateCheckStatus.skipped:
            skipped.append(check.check_id)
            continue
        definition = get_gate_check_definition(check.check_id)
        if definition is not None and definition.required and check.status != GateCheckStatus.pass_:
            blocked_by.append(check.check_id)

    return ReleaseGateResult(
        approved=len(blocked_by) == 0,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
        checks=checks,
        blocked_by=blocked_by,
        skipped=skipped,
    )


def is_gate_approved(result: ReleaseGateResult) -> bool:
    """Returns whether the gate is fully approved (all required checks pass)."""
    return result.approved
