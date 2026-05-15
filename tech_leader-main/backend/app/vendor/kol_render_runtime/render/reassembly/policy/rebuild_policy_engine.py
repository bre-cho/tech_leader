from __future__ import annotations

from typing import Any


class RebuildPolicyEngine:
    """Policy engine with required/optional/skip semantics."""

    REQUIRED_TYPES = {"self", "timeline"}
    REQUIRED_STRENGTH = 0.85
    OPTIONAL_STRENGTH = 0.50

    def classify_scene(
        self,
        *,
        scene_id: str,
        reasons: list[dict[str, Any]],
        force_quality: bool = False,
    ) -> dict[str, Any]:
        max_strength = max((float(r.get("strength", 0.0) or 0.0) for r in reasons), default=0.0)
        reason_types = {str(r.get("dependency_type") or "") for r in reasons}

        if force_quality and reasons:
            decision = "required"
        elif reason_types.intersection(self.REQUIRED_TYPES) or max_strength >= self.REQUIRED_STRENGTH:
            decision = "required"
        elif max_strength >= self.OPTIONAL_STRENGTH:
            decision = "optional"
        else:
            decision = "skip"

        return {
            "scene_id": scene_id,
            "decision": decision,
            "max_strength": max_strength,
            "reason_count": len(reasons),
            "reason_types": sorted(rt for rt in reason_types if rt),
        }

    def classify_many(
        self,
        *,
        reason_report: dict[str, list[dict[str, Any]]],
        force_quality: bool = False,
    ) -> dict[str, dict[str, Any]]:
        return {
            scene_id: self.classify_scene(
                scene_id=scene_id,
                reasons=list(reasons or []),
                force_quality=force_quality,
            )
            for scene_id, reasons in reason_report.items()
        }

    def required_scene_ids(self, policy_report: dict[str, dict[str, Any]]) -> list[str]:
        return [scene_id for scene_id, details in policy_report.items() if details.get("decision") == "required"]

    def optional_scene_ids(self, policy_report: dict[str, dict[str, Any]]) -> list[str]:
        return [scene_id for scene_id, details in policy_report.items() if details.get("decision") == "optional"]

    def skipped_scene_ids(self, policy_report: dict[str, dict[str, Any]]) -> list[str]:
        return [scene_id for scene_id, details in policy_report.items() if details.get("decision") == "skip"]
