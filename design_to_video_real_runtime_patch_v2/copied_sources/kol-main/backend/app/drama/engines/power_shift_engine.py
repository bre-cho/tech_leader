from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Optional


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


class PowerShiftEngine:
    """Computes scene outcome deltas across multiple power dimensions.

    Multipliers are tunable via environment variables so operations teams can
    adjust dramatic sensitivity without a code deploy:

    ========================================  =========  ========
    Env var                                   Default    Effect
    ========================================  =========  ========
    ``POWER_SHIFT_SOCIAL_MULT``               ``-0.10``  Social delta per dominance unit
    ``POWER_SHIFT_EMOTIONAL_MULT``            ``0.20``   Emotional delta per exposure unit
    ``POWER_SHIFT_INFORMATIONAL_MULT``        ``0.15``   Informational delta per exposure unit
    ``POWER_SHIFT_NARRATIVE_CONTROL_DEFAULT`` ``0.10``   Default narrative control delta
    ``POWER_SHIFT_TRUST_DELTA``               ``-0.05``  Trust shift in relationship updates
    ========================================  =========  ========
    """

    def compute(
        self,
        scene_context: Optional[Dict[str, Any]] = None,
        relationship_snapshots: Optional[Iterable[Any]] = None,
    ) -> Dict[str, Any]:
        scene_context = scene_context or {}
        relationships = list(relationship_snapshots or [])

        avg_dom = 0.0
        if relationships:
            avg_dom = sum(float(getattr(r, "dominance_source_over_target", 0.0) or 0.0) for r in relationships) / len(relationships)

        trigger = scene_context.get("trigger_event", "scene_turn")
        exposure_risk = float(scene_context.get("exposure_risk", 0.3))

        social_mult = _env_float("POWER_SHIFT_SOCIAL_MULT", -0.10)
        emotional_mult = _env_float("POWER_SHIFT_EMOTIONAL_MULT", 0.20)
        informational_mult = _env_float("POWER_SHIFT_INFORMATIONAL_MULT", 0.15)
        narrative_control_default = _env_float("POWER_SHIFT_NARRATIVE_CONTROL_DEFAULT", 0.10)
        trust_delta = _env_float("POWER_SHIFT_TRUST_DELTA", -0.05)

        social_delta = round(avg_dom * social_mult, 3)
        emotional_delta = round(exposure_risk * emotional_mult, 3)
        informational_delta = round(exposure_risk * informational_mult, 3)
        moral_delta = round(scene_context.get("moral_reversal", 0.0), 3)
        spatial_delta = round(scene_context.get("spatial_shift", 0.0), 3)
        narrative_control_delta = round(scene_context.get("narrative_control_shift", narrative_control_default), 3)

        total_delta = sum(abs(x) for x in [
            social_delta,
            emotional_delta,
            informational_delta,
            moral_delta,
            spatial_delta,
            narrative_control_delta,
        ])

        dominant_character_id = scene_context.get("dominant_character_id")
        threatened_character_id = scene_context.get("threatened_character_id")

        # Infer threatened character from participants if not explicitly set.
        if dominant_character_id and not threatened_character_id:
            for participant in scene_context.get("participants", []):
                cid = str(participant.get("character_id") or participant.get("id") or "")
                if cid and cid != str(dominant_character_id):
                    threatened_character_id = cid
                    break

        relationship_shifts: list = []
        if dominant_character_id and threatened_character_id:
            relationship_shifts = [
                {
                    "source": dominant_character_id,
                    "target": threatened_character_id,
                    "trust_delta": trust_delta,
                    "resentment_delta": min(0.2, total_delta),
                    "dominance_delta": social_delta,
                }
            ]

        return {
            "trigger_event": trigger,
            "social_delta": social_delta,
            "emotional_delta": emotional_delta,
            "informational_delta": informational_delta,
            "moral_delta": moral_delta,
            "spatial_delta": spatial_delta,
            "narrative_control_delta": narrative_control_delta,
            "total_delta": round(total_delta, 3),
            "dominant_character_id": dominant_character_id,
            "threatened_character_id": threatened_character_id,
            "relationship_shifts": relationship_shifts,
        }
