from __future__ import annotations

from typing import Any
from app.governance.agent_permissions import get_permissions

_RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class TrustPolicyEnforcer:
    """Enforce agent permission contracts before every action."""

    def check_action(
        self,
        agent_name: str,
        action_type: str,
        resource: str,
        *,
        decision_logger=None,
        workflow_id: str = "unknown",
    ) -> dict[str, Any]:
        """
        Returns {"allowed": bool, "reason": str}.

        action_type: "tool_use" | "memory_write" | "artifact_produce"
        resource:    the tool name / memory layer / artifact type being accessed
        """
        perms = get_permissions(agent_name)
        allowed, reason = self._evaluate(action_type, resource, perms)

        result = {"allowed": allowed, "reason": reason}

        if decision_logger is not None:
            decision_logger.log(
                workflow_id=workflow_id,
                decision_type=f"trust_policy.{action_type}",
                outcome="ALLOWED" if allowed else "DENIED",
                reason=reason,
                metadata={"agent_name": agent_name, "resource": resource},
            )

        return result

    # ------------------------------------------------------------------
    def _evaluate(
        self, action_type: str, resource: str, perms: dict[str, Any]
    ) -> tuple[bool, str]:
        if action_type == "tool_use":
            if resource in perms["allowed_tools"]:
                return True, f"tool '{resource}' is in allowed_tools"
            return False, f"tool '{resource}' not in allowed_tools for this agent"

        if action_type == "memory_write":
            if resource in perms["allowed_memory_writes"]:
                return True, f"memory layer '{resource}' is permitted"
            return False, f"memory layer '{resource}' not permitted for this agent"

        if action_type == "artifact_produce":
            if resource in perms["allowed_artifact_types"]:
                return True, f"artifact type '{resource}' is permitted"
            return False, f"artifact type '{resource}' not permitted for this agent"

        if action_type == "risk_level":
            requested = _RISK_ORDER.get(resource, 99)
            allowed_max = _RISK_ORDER.get(perms["max_risk_level"], 0)
            if requested <= allowed_max:
                return True, f"risk level '{resource}' is within budget"
            return False, f"risk level '{resource}' exceeds max_risk_level '{perms['max_risk_level']}'"

        # Unknown action type – deny by default
        return False, f"unknown action_type '{action_type}' — denied by default"
