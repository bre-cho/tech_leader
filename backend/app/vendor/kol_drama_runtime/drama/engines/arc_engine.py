from __future__ import annotations

from typing import Any, Dict

# Tension thresholds for early-arc stage progression.
# These can be tuned without code changes if re-exposed as env vars in future.
_PRESSURE_CRACK_TENSION_THRESHOLD: float = 50.0
_DEFENSIVE_ESCALATION_TENSION_THRESHOLD: float = 65.0
_FIRST_EXPOSURE_EXPOSURE_RISK_THRESHOLD: float = 0.75
_COLLAPSE_TENSION_THRESHOLD: float = 75.0
_TRUTH_ENCOUNTER_ACCEPTANCE_THRESHOLD: float = 0.7
_REORGANIZATION_TRANSFORMATION_THRESHOLD: float = 0.7
_TRANSFORMED_STATE_ACCEPTANCE_THRESHOLD: float = 0.9


class ArcEngine:
    """Advances character arc stages using explainable scene outcome rules."""

    ARC_ORDER = [
        "mask_stable",
        "pressure_crack",
        "defensive_escalation",
        "first_exposure",
        "collapse_or_rupture",
        "truth_encounter",
        "reorganization",
        "transformed_state",
    ]

    def advance_arc(
        self,
        character_arc_state: Dict[str, Any],
        scene_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        current_stage = character_arc_state.get("arc_stage", "mask_stable")
        tension_score = float(scene_analysis.get("tension_breakdown", {}).get("tension_score", 0.0))
        exposure_risk = float(scene_analysis.get("tension_breakdown", {}).get("exposure_risk", 0.0))
        outcome_type = scene_analysis.get("power_shift", {}).get("outcome_type")

        truth_acceptance = float(character_arc_state.get("truth_acceptance_level", 0.0))
        transformation_idx = float(character_arc_state.get("transformation_index", 0.0))

        next_stage = current_stage
        # High exposure risk breaks through the mask regardless of arc stage —
        # this is a skip-ahead that takes priority over the gradual progression
        # rules below.  ArcEngine tests rely on this behaviour.
        if exposure_risk > _FIRST_EXPOSURE_EXPOSURE_RISK_THRESHOLD and current_stage in {"mask_stable", "pressure_crack", "defensive_escalation"}:
            next_stage = "first_exposure"
        # Gradual early-arc progression — mask shows cracks under pressure,
        # then the character escalates defensively.  Only applied when the
        # skip-ahead above does not fire.
        elif current_stage == "mask_stable" and tension_score > _PRESSURE_CRACK_TENSION_THRESHOLD:
            next_stage = "pressure_crack"
        elif current_stage == "pressure_crack" and tension_score > _DEFENSIVE_ESCALATION_TENSION_THRESHOLD:
            next_stage = "defensive_escalation"
        elif outcome_type in {"moral_power_flip", "dominance_flip"} and tension_score > _COLLAPSE_TENSION_THRESHOLD:
            next_stage = "collapse_or_rupture"
        elif truth_acceptance > _TRUTH_ENCOUNTER_ACCEPTANCE_THRESHOLD and current_stage not in {"reorganization", "transformed_state"}:
            next_stage = "truth_encounter"
        elif current_stage == "truth_encounter" and transformation_idx > _REORGANIZATION_TRANSFORMATION_THRESHOLD:
            next_stage = "reorganization"
        elif current_stage == "reorganization" and truth_acceptance > _TRANSFORMED_STATE_ACCEPTANCE_THRESHOLD:
            next_stage = "transformed_state"

        return {
            "character_id": character_arc_state.get("character_id"),
            "previous_stage": current_stage,
            "next_stage": next_stage,
            "pressure_index": min(1.0, float(character_arc_state.get("pressure_index", 0.0)) + tension_score / 200.0),
            "transformation_index": self._transformation_index(character_arc_state, next_stage),
            "notes": self._notes(current_stage, next_stage),
        }

    def _transformation_index(self, character_arc_state: Dict[str, Any], next_stage: str) -> float:
        base = float(character_arc_state.get("transformation_index", 0.0))
        if next_stage != character_arc_state.get("arc_stage"):
            return min(1.0, base + 0.15)
        return base

    def _notes(self, current_stage: str, next_stage: str):
        if current_stage == next_stage:
            return ["Arc remains in current stage; preserve continuity rather than forcing visible change."]
        return [f"Advance arc from {current_stage} to {next_stage} with a readable transition beat."]
