from __future__ import annotations

from typing import Any


class RebuildCostEstimator:
    def estimate_scene(self, scene_manifest: dict[str, Any], change_type: str = "subtitle") -> dict[str, Any]:
        duration = float(scene_manifest.get("duration_sec") or scene_manifest.get("target_duration_sec") or 6.0)
        base_cost = max(0.05, duration * 0.02)
        multiplier = 1.0
        if change_type in {"voice", "avatar", "style"}:
            multiplier = 1.5
        elif change_type == "all":
            multiplier = 2.0
        estimated_cost = round(base_cost * multiplier, 4)
        estimated_time_sec = round(max(5.0, duration * (2.0 if multiplier > 1.0 else 1.2)), 2)
        return {
            "scene_id": scene_manifest.get("scene_id"),
            "estimated_cost": estimated_cost,
            "estimated_time_sec": estimated_time_sec,
            "change_type": change_type,
        }
