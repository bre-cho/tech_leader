from __future__ import annotations

from typing import Any

from app.render.reassembly.optimizer.rebuild_cost_estimator import RebuildCostEstimator


class RebuildStrategyOptimizer:
    def __init__(self) -> None:
        self._estimator = RebuildCostEstimator()

    def _estimate(self, scene_ids: list[str], manifests_by_id: dict[str, dict[str, Any]], change_type: str) -> tuple[float, float]:
        total_cost = 0.0
        total_time = 0.0
        for sid in scene_ids:
            estimate = self._estimator.estimate_scene(manifests_by_id.get(sid, {"scene_id": sid}), change_type=change_type)
            total_cost += float(estimate["estimated_cost"])
            total_time += float(estimate["estimated_time_sec"])
        return round(total_cost, 4), round(total_time, 2)

    def choose_strategy(
        self,
        *,
        all_manifests: list[dict[str, Any]],
        changed_scene_id: str,
        required_scene_ids: list[str],
        optional_scene_ids: list[str],
        affected_range_scene_ids: list[str],
        change_type: str,
        has_timeline_drift: bool,
        force_full_rebuild: bool,
        include_optional: bool,
    ) -> dict[str, Any]:
        manifests_by_id = {str(item.get("scene_id")): item for item in all_manifests}
        all_scene_ids = [str(item.get("scene_id")) for item in all_manifests if item.get("scene_id")]

        safe_minimum_ids = sorted(set(required_scene_ids) | {changed_scene_id})
        if has_timeline_drift and affected_range_scene_ids:
            safe_minimum_ids = sorted(set(safe_minimum_ids) | set(affected_range_scene_ids))

        balanced_ids = sorted(set(safe_minimum_ids) | (set(optional_scene_ids) if include_optional else set()))
        full_ids = sorted(set(all_scene_ids))

        candidates: list[dict[str, Any]] = []
        for name, ids, safe in (
            ("safe_minimum", safe_minimum_ids, True),
            ("balanced_optional", balanced_ids, True),
            ("full_rebuild", full_ids, True),
        ):
            cost, eta = self._estimate(ids, manifests_by_id, change_type)
            candidates.append(
                {
                    "strategy": name,
                    "scene_ids": ids,
                    "estimated_cost": cost,
                    "estimated_time_sec": eta,
                    "safe": safe,
                    "reason": f"{name} strategy",
                }
            )

        if force_full_rebuild:
            chosen = next(item for item in candidates if item["strategy"] == "full_rebuild")
        else:
            chosen = min(candidates, key=lambda item: (len(item["scene_ids"]), item["estimated_cost"]))

        return {
            "candidates": candidates,
            "chosen_strategy": chosen,
        }
