from __future__ import annotations

from typing import Any


class ExecutionBudgetGuard:
    def enforce(
        self,
        *,
        optimization: dict[str, Any],
        max_cost: float,
        max_time_sec: float,
        allow_downgrade: bool,
    ) -> dict[str, Any]:
        chosen = dict(optimization.get("chosen_strategy") or {})
        candidates = list(optimization.get("candidates") or [])

        def _within_budget(item: dict[str, Any]) -> bool:
            return float(item.get("estimated_cost", 0.0)) <= float(max_cost) and float(
                item.get("estimated_time_sec", 0.0)
            ) <= float(max_time_sec)

        if chosen and _within_budget(chosen):
            return {
                "allowed": True,
                "action": "allow",
                "reason": "Selected strategy is within budget.",
                "chosen_strategy": chosen,
                "original_strategy": chosen,
                "budget": {"max_cost": float(max_cost), "max_time_sec": float(max_time_sec)},
            }

        fallback = None
        if allow_downgrade:
            in_budget = [item for item in candidates if _within_budget(item)]
            if in_budget:
                fallback = min(in_budget, key=lambda item: (float(item.get("estimated_cost", 0.0)), len(item.get("scene_ids", []))))

        if fallback is not None:
            return {
                "allowed": True,
                "action": "downgrade",
                "reason": "Selected strategy exceeded budget; downgraded to in-budget candidate.",
                "chosen_strategy": fallback,
                "original_strategy": chosen,
                "budget": {"max_cost": float(max_cost), "max_time_sec": float(max_time_sec)},
            }

        return {
            "allowed": False,
            "action": "block",
            "reason": "No strategy satisfies budget constraints.",
            "chosen_strategy": chosen,
            "original_strategy": chosen,
            "budget": {"max_cost": float(max_cost), "max_time_sec": float(max_time_sec)},
        }
