from __future__ import annotations

import os
from typing import Any, Dict


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


class EmotionalUpdateEngine:
    """Applies outcome-driven emotional shifts on top of a prior character state.

    Deltas are tunable via environment variables so operations teams can adjust
    dramatic sensitivity without a code deploy:

    =============================================  ==========  ========
    Env var                                        Default     Effect
    =============================================  ==========  ========
    ``BETRAYAL_EMOTIONAL_TRUST_DELTA``             ``-0.20``   Extra trust penalty on betrayal
    ``BETRAYAL_EMOTIONAL_EXPOSURE_DELTA``          ``0.15``    Extra exposure on betrayal
    ``CONFESSION_EMOTIONAL_TRUST_DELTA``           ``0.15``    Trust gain on confession
    ``CONFESSION_EMOTIONAL_EXPOSURE_DELTA``        ``0.10``    Exposure increase on confession
    ``FORGIVENESS_EMOTIONAL_TRUST_DELTA``          ``0.12``    Trust gain on forgiveness/reconciliation
    ``FORGIVENESS_EMOTIONAL_EXPOSURE_DELTA``       ``0.08``    Exposure increase on forgiveness
    ``CATHARSIS_EMOTIONAL_TRUST_DELTA``            ``0.08``    Trust gain on catharsis/resolution
    ``CATHARSIS_EMOTIONAL_EXPOSURE_DELTA``         ``0.12``    Exposure increase on catharsis
    =============================================  ==========  ========
    """

    def apply(self, previous_state: Dict[str, Any], outcome: Dict[str, Any]) -> Dict[str, Any]:
        next_state = dict(previous_state or {})
        outcome_type = (outcome.get("outcome_type") or "").lower()

        trust_delta = float(outcome.get("trust_shift_delta", 0.0) or 0.0)
        exposure_delta = float(outcome.get("exposure_shift_delta", 0.0) or 0.0)

        if outcome_type == "betrayal":
            trust_delta += _env_float("BETRAYAL_EMOTIONAL_TRUST_DELTA", -0.20)
            exposure_delta += _env_float("BETRAYAL_EMOTIONAL_EXPOSURE_DELTA", 0.15)
        elif outcome_type == "confession":
            trust_delta += _env_float("CONFESSION_EMOTIONAL_TRUST_DELTA", 0.15)
            exposure_delta += _env_float("CONFESSION_EMOTIONAL_EXPOSURE_DELTA", 0.10)
        elif outcome_type in {"forgiveness", "reconciliation"}:
            trust_delta += _env_float("FORGIVENESS_EMOTIONAL_TRUST_DELTA", 0.12)
            exposure_delta += _env_float("FORGIVENESS_EMOTIONAL_EXPOSURE_DELTA", 0.08)
        elif outcome_type in {"catharsis", "resolution"}:
            trust_delta += _env_float("CATHARSIS_EMOTIONAL_TRUST_DELTA", 0.08)
            exposure_delta += _env_float("CATHARSIS_EMOTIONAL_EXPOSURE_DELTA", 0.12)

        next_state["trust_level"] = max(0.0, min(1.0, float(next_state.get("trust_level", 0.5)) + trust_delta))
        next_state["mask_strength"] = max(0.0, min(1.0, float(next_state.get("mask_strength", 0.5)) - max(0.0, exposure_delta)))
        next_state["openness_level"] = max(0.0, min(1.0, float(next_state.get("openness_level", 0.5)) + max(0.0, exposure_delta * 0.5)))
        return next_state
