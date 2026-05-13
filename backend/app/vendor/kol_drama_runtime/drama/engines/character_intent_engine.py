from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.core.production_gate import ensure_stub_allowed
from app.drama.engines._model_path import get_drama_model_path

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model integration
# ---------------------------------------------------------------------------
# When DRAMA_INTENT_MODEL_PATH is set and points to a valid joblib artifact,
# CharacterIntentEngine delegates to ml/serving.predict_from_artifact() for
# intent classification instead of the heuristic string-building logic.
#
# To activate:
#   1. Train a drama-intent model (features → intent class score).
#   2. Save it with: joblib.dump(model, "<path>/drama_intent_model.joblib")
#   3. Set DRAMA_INTENT_MODEL_PATH=<path>/drama_intent_model.joblib
#
# Monitor: Prometheus metric `character_intent_engine_placeholder` is 1 while
# the heuristic path is active so ops know the model has not been trained.
# ---------------------------------------------------------------------------

CHARACTER_INTENT_ENGINE_PLACEHOLDER: bool = True  # flipped False when model active
# Lock protecting both writes AND reads of CHARACTER_INTENT_ENGINE_PLACEHOLDER so
# that concurrent workers see a consistent value when the model first loads.
_PLACEHOLDER_LOCK: threading.Lock = threading.Lock()
_placeholder_state: dict[str, bool] = {"value": True}

_INTENT_MODEL_PATH = os.environ.get("DRAMA_INTENT_MODEL_PATH", "").strip()


def _set_character_intent_engine_placeholder(value: bool) -> None:
    global CHARACTER_INTENT_ENGINE_PLACEHOLDER
    with _PLACEHOLDER_LOCK:
        _placeholder_state["value"] = value
        CHARACTER_INTENT_ENGINE_PLACEHOLDER = value


def is_character_intent_engine_placeholder() -> bool:
    """Return the current value of :data:`CHARACTER_INTENT_ENGINE_PLACEHOLDER` under lock.

    Use this instead of reading the global directly when the caller needs a
    consistent snapshot (e.g. Prometheus metrics collection in a multi-worker
    environment).
    """
    with _PLACEHOLDER_LOCK:
        return _placeholder_state["value"]

_INTENT_LABELS = [
    "advance_outer_goal",
    "pursue_scene_goal",
    "protect_self_position",
    "exploit_vulnerability",
    "seek_validation",
    "deflect_threat",
]


_INTENT_FEATURE_SCHEMA = [
    "has_outer_goal",
    "has_beat_goal",
    "has_hidden_need",
    "has_dominant_fear",
    "has_mask_strategy",
    "exposure_risk",
]


def _try_model_intent(features: Dict[str, Any]) -> str | None:
    """Attempt intent classification via ml/serving.predict_from_artifact().

    Returns one of the ``_INTENT_LABELS`` strings, or ``None`` when no model
    is configured or inference fails.  Failure is non-fatal; the heuristic
    fallback is used and the placeholder flag stays ``True``.
    """
    model_path = get_drama_model_path("DRAMA_INTENT_MODEL_PATH") or _INTENT_MODEL_PATH
    if not model_path:
        _set_character_intent_engine_placeholder(True)
        return None
    try:
        from app.ml.serving import predict_from_artifact  # noqa: PLC0415

        result = predict_from_artifact(model_path, features, feature_schema=_INTENT_FEATURE_SCHEMA)
        if result.stub:
            ensure_stub_allowed("Drama character intent model stub fallback", allow_env="ALLOW_DRAMA_MODEL_STUB")
            _set_character_intent_engine_placeholder(True)
            return None
        raw_score = float(result.score)
        # Map score ∈ [0, 1] to a label index.  Clamp explicitly so that
        # raw_score=1.0 always maps to the last label rather than relying
        # on the min() overflow guard.
        label_idx = max(0, min(len(_INTENT_LABELS) - 1, int(raw_score * len(_INTENT_LABELS))))
        _set_character_intent_engine_placeholder(False)
        return _INTENT_LABELS[label_idx]
    except Exception as exc:  # noqa: BLE001
        _set_character_intent_engine_placeholder(True)
        _logger.debug("CharacterIntentEngine: model inference failed (%s); using heuristic", exc)
        return None


@dataclass
class CharacterIntentResult:
    character_id: str
    outer_goal: Optional[str]
    hidden_need: Optional[str]
    fear_trigger: Optional[str]
    mask_strategy: Optional[str]
    likely_scene_intent: str
    pressure_response: Optional[str]
    notes: List[str]


class CharacterIntentEngine:
    """Derives per-character scene intent from profile + optional beat context.

    When ``DRAMA_INTENT_MODEL_PATH`` points to a trained joblib artifact the
    intent label is produced by the ML model via
    ``ml/serving.predict_from_artifact()``.  Otherwise, heuristic string
    composition is used and :data:`CHARACTER_INTENT_ENGINE_PLACEHOLDER` stays
    ``True`` to signal that a real model should be trained and registered.

    Monitor via Prometheus: ``character_intent_engine_placeholder == 1`` means
    only heuristic intent strings are being produced.

    The goal here is not to generate prose, but to give downstream engines a
    compact, machine-readable intent package.
    """

    def derive(self, profile: Any, scene_context: Optional[Dict[str, Any]] = None) -> CharacterIntentResult:
        scene_context = scene_context or {}
        beat_goal = scene_context.get("scene_goal")

        # Build a feature dict for the optional ML path.
        features = {
            "has_outer_goal": 1.0 if getattr(profile, "outer_goal", None) else 0.0,
            "has_beat_goal": 1.0 if beat_goal else 0.0,
            "has_hidden_need": 1.0 if getattr(profile, "hidden_need", None) else 0.0,
            "has_dominant_fear": 1.0 if getattr(profile, "dominant_fear", None) else 0.0,
            "has_mask_strategy": 1.0 if getattr(profile, "mask_strategy", None) else 0.0,
            "exposure_risk": float(scene_context.get("exposure_risk", 0.3)),
        }
        model_label = _try_model_intent(features)

        if model_label is not None:
            likely_scene_intent = self._label_to_intent(model_label, profile, beat_goal)
        elif beat_goal and getattr(profile, "outer_goal", None):
            likely_scene_intent = f"Pursue outer goal through scene goal: {beat_goal}"
        elif getattr(profile, "outer_goal", None):
            likely_scene_intent = f"Advance outer goal: {profile.outer_goal}"
        else:
            likely_scene_intent = "Probe scene and protect self-position"

        notes: List[str] = []
        if getattr(profile, "dominant_fear", None):
            notes.append(f"Avoid trigger: {profile.dominant_fear}")
        if getattr(profile, "public_persona", None) and getattr(profile, "private_self", None):
            notes.append("Mask tension present between public persona and private self")

        return CharacterIntentResult(
            character_id=str(profile.id),
            outer_goal=getattr(profile, "outer_goal", None),
            hidden_need=getattr(profile, "hidden_need", None),
            fear_trigger=getattr(profile, "dominant_fear", None),
            mask_strategy=getattr(profile, "mask_strategy", None),
            likely_scene_intent=likely_scene_intent,
            pressure_response=getattr(profile, "pressure_response", None),
            notes=notes,
        )

    @staticmethod
    def _label_to_intent(label: str, profile: Any, beat_goal: Optional[str]) -> str:
        """Translate a model label back to a human-readable intent string."""
        if label == "pursue_scene_goal" and beat_goal:
            return f"Pursue outer goal through scene goal: {beat_goal}"
        if label == "advance_outer_goal" and getattr(profile, "outer_goal", None):
            return f"Advance outer goal: {profile.outer_goal}"
        label_to_text = {
            "protect_self_position": "Probe scene and protect self-position",
            "exploit_vulnerability": "Exploit perceived vulnerability in the other party",
            "seek_validation": "Seek recognition or validation of inner worth",
            "deflect_threat": "Deflect incoming threat through misdirection",
        }
        return label_to_text.get(label, "Probe scene and protect self-position")
