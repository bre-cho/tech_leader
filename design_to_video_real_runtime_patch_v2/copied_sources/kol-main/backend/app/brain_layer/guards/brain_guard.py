"""brain_layer/guards/brain_guard.py — brain-layer approval shim.

.. deprecated::
    This module is a **no-op shim** that unconditionally approves every
    decision.  It exists as a backward-compatible placeholder from an earlier
    design where a dedicated brain-layer service was planned.

    Do NOT add real business logic here.  If you need a real approval gate,
    implement it in the calling service with explicit policy rules, or wire in
    a proper policy engine (e.g. OPA, a database-backed rule set, or the
    ``AvatarPolicyEngine``).

    Planned removal: this module will be removed in Q4/2026 once all callers
    have been migrated to service-specific approval logic.  Track usage with::

        grep -r "brain_guard" backend/app --include="*.py"
"""
from __future__ import annotations

import uuid
import warnings
from typing import Any


def _check_kill_switch_gate(action: str) -> tuple[bool, str]:
    """Check the kill switch for the given action gate.

    Returns (approved, reason).  When Redis/DB is unavailable the kill switch
    defaults to ``True`` (enabled), meaning the action is permitted.
    """
    try:
        from app.services.kill_switch import get_or_create_global_kill_switch  # noqa: PLC0415
        ks = get_or_create_global_kill_switch()
        gate_key = f"brain_gate.{action}"
        enabled = ks.is_enabled(gate_key)
        if not enabled:
            return False, f"brain_gate.{action} kill-switch is disabled"
    except Exception:  # noqa: BLE001
        pass  # Fail open: kill-switch unavailable → allow
    return True, "kill-switch gate passed"


def require_brain_decision(context: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """Return a policy-checked decision with a stable ``decision_id``.

    Checks the ``brain_gate.<action>`` kill switch; raises ``RuntimeError``
    when the gate is disabled.

    .. deprecated::
        Implement real approval logic in the calling service instead of
        relying on this function.  Planned removal: Q4/2026.
    """
    warnings.warn(
        "require_brain_decision() is a no-op shim. "
        "Implement explicit approval logic in the calling service. "
        "Planned removal: Q4/2026.",
        DeprecationWarning,
        stacklevel=2,
    )
    action = str(kwargs.get("action") or context or "unknown")
    approved, reason = _check_kill_switch_gate(action)
    if not approved:
        raise RuntimeError(
            f"Brain gate denied: {reason}. "
            "Re-enable the gate via KillSwitchService or implement policy-level approval."
        )
    decision_id = str(uuid.uuid4())
    return {
        "approved": True,
        "decision_id": decision_id,
        "reason": reason,
        "context": context,
        "inputs": kwargs,
    }


def require_brain_decision_for_worker(worker_name: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """Return a policy-checked decision for a Celery worker context.

    Checks the ``brain_gate.<action>`` kill switch; raises ``RuntimeError``
    when the gate is disabled.

    .. deprecated::
        Implement explicit approval logic in the worker instead of relying on
        this function.  Planned removal: Q4/2026.
    """
    warnings.warn(
        "require_brain_decision_for_worker() is a no-op shim. "
        "Implement explicit approval logic in the worker instead. "
        "Planned removal: Q4/2026.",
        DeprecationWarning,
        stacklevel=2,
    )
    action = str(kwargs.get("action") or worker_name or "worker")
    approved, reason = _check_kill_switch_gate(action)
    if not approved:
        raise RuntimeError(
            f"Brain gate denied for worker: {reason}. "
            "Re-enable the gate via KillSwitchService or implement policy-level approval."
        )
    decision_id = str(uuid.uuid4())
    return {
        "approved": True,
        "decision_id": decision_id,
        "reason": reason,
        "context": worker_name or "worker",
        "inputs": kwargs,
    }
