from __future__ import annotations

import logging
import os
import threading
from typing import Any, Dict, Optional

from app.core.production_gate import ensure_stub_allowed
from app.drama.engines._model_path import get_drama_model_path

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Placeholder flag
# ---------------------------------------------------------------------------
# SubtextEngine uses rule-based action selection when no trained model is
# available.
#
# To activate a real model:
#   1. Train a multi-label subtext model via ml/training/drama_subtext_trainer.py.
#   2. Save it with: joblib.dump(model, "<path>/subtext_model.joblib")
#   3. Set DRAMA_SUBTEXT_MODEL_PATH=<path>/subtext_model.joblib
#
# The model outputs 5 binary labels:
#   [denial, deflection, sarcasm, suppression, vulnerability_exposure]
# which are mapped to a psychological_action.
#
# Monitor: Prometheus metric `subtext_engine_placeholder` is 1 while the
# rule-based path is active so ops know a real model has not yet been deployed.
# ---------------------------------------------------------------------------

SUBTEXT_ENGINE_PLACEHOLDER: bool = True  # flipped to False when a real model loads
# Lock protecting both writes AND reads of SUBTEXT_ENGINE_PLACEHOLDER so
# that concurrent workers see a consistent value when the model first loads.
_PLACEHOLDER_LOCK: threading.Lock = threading.Lock()
_placeholder_state: dict[str, bool] = {"value": True}

_MODEL_PATH = os.environ.get("DRAMA_SUBTEXT_MODEL_PATH", "").strip()


def _set_subtext_engine_placeholder(value: bool) -> None:
    global SUBTEXT_ENGINE_PLACEHOLDER
    with _PLACEHOLDER_LOCK:
        _placeholder_state["value"] = value
        SUBTEXT_ENGINE_PLACEHOLDER = value


def is_subtext_engine_placeholder() -> bool:
    """Return the current value of :data:`SUBTEXT_ENGINE_PLACEHOLDER` under lock.

    Use this instead of reading the global directly when the caller needs a
    consistent snapshot (e.g. Prometheus metrics collection in a multi-worker
    environment).
    """
    with _PLACEHOLDER_LOCK:
        return _placeholder_state["value"]

# Label index constants matching drama_subtext_trainer._LABEL_COLUMNS order.
_LABEL_DENIAL = 0
_LABEL_DEFLECTION = 1
_LABEL_SARCASM = 2
_LABEL_SUPPRESSION = 3
_LABEL_VULNERABILITY = 4

# Map from dominant active label to (psychological_action, hidden_intent).
_LABEL_TO_ACTION: dict[int, tuple[str, str]] = {
    _LABEL_SARCASM: ("attack", "Punish while maintaining plausible deniability"),
    _LABEL_SUPPRESSION: ("dominate", "Narrow the other character's perceived options"),
    _LABEL_VULNERABILITY: ("reassure", "Stabilize alliance and preserve emotional access"),
    _LABEL_DENIAL: ("redirect", "Change frame before accountability lands"),
    _LABEL_DEFLECTION: ("probe", "Shift scrutiny without accepting responsibility"),
}


_MANIPULATION_ARCHETYPE_SCORE = 8.0   # high manipulation score for Manipulator archetype
_MANIPULATION_DEFAULT_SCORE = 2.0    # baseline for all other archetypes

def _build_subtext_features(
    trust: float,
    resentment: float,
    dominance: float,
    archetype: str | None,
    scene_context: dict[str, Any],
) -> dict[str, float]:
    """Build an 11-dimensional feature dict matching drama_subtext_trainer schema.

    Feature order must match *_FEATURE_COLUMNS* in drama_subtext_trainer.py:
      denial_score, deflection_score, sarcasm_score, suppression_score,
      manipulation_score, vulnerability_score, power_play_score, irony_score,
      scene_tension_score, power_imbalance_score, truth_score
    """
    # Derive proxy scores (scale ×10 to match [0, 10] trainer range)
    denial_score = (1.0 - trust) * 7.0
    deflection_score = (1.0 - trust) * 5.0 + resentment * 3.0
    sarcasm_score = resentment * 8.0
    suppression_score = max(0.0, dominance) * 7.0
    manipulation_score = _MANIPULATION_ARCHETYPE_SCORE if (archetype or "").lower() == "manipulator" else _MANIPULATION_DEFAULT_SCORE
    vulnerability_score = float(scene_context.get("exposure_risk", 0.3)) * 10.0
    power_play_score = abs(dominance) * 7.0
    irony_score = resentment * 5.0 + (1.0 - trust) * 3.0
    scene_tension_score = float(scene_context.get("exposure_risk", 0.3)) * 10.0
    power_imbalance_score = abs(dominance) * 10.0
    truth_score = trust * 10.0
    return {
        "denial_score": denial_score,
        "deflection_score": deflection_score,
        "sarcasm_score": sarcasm_score,
        "suppression_score": suppression_score,
        "manipulation_score": manipulation_score,
        "vulnerability_score": vulnerability_score,
        "power_play_score": power_play_score,
        "irony_score": irony_score,
        "scene_tension_score": scene_tension_score,
        "power_imbalance_score": power_imbalance_score,
        "truth_score": truth_score,
    }


def _labels_to_action(labels: list[int]) -> tuple[str, str]:
    """Map 5 binary labels to a (psychological_action, hidden_intent) pair.

    Priority order matches psychological intensity (sarcasm > suppression >
    vulnerability > denial > deflection).  When no label is active the
    default probe action is returned.
    """
    priority = [
        _LABEL_SARCASM,
        _LABEL_SUPPRESSION,
        _LABEL_VULNERABILITY,
        _LABEL_DENIAL,
        _LABEL_DEFLECTION,
    ]
    for idx in priority:
        if idx < len(labels) and labels[idx]:
            return _LABEL_TO_ACTION[idx]
    return "probe", "Test the other character's position"


_SUBTEXT_FEATURE_SCHEMA = [
    "denial_score",
    "deflection_score",
    "sarcasm_score",
    "suppression_score",
    "manipulation_score",
    "vulnerability_score",
    "power_play_score",
    "irony_score",
    "scene_tension_score",
    "power_imbalance_score",
    "truth_score",
]


def _try_model_subtext(
    trust: float,
    resentment: float,
    dominance: float,
    archetype: str | None,
    scene_context: dict[str, Any],
) -> tuple[str, str] | None:
    """Attempt (psychological_action, hidden_intent) via the trained model.

    Returns a tuple on success, or ``None`` when no model is configured or
    inference fails so the rule-based fallback is used instead.
    """
    model_path = get_drama_model_path("DRAMA_SUBTEXT_MODEL_PATH") or _MODEL_PATH
    if not model_path:
        _set_subtext_engine_placeholder(True)
        return None
    try:
        from app.ml.serving import predict_labels_from_artifact  # noqa: PLC0415

        features = _build_subtext_features(trust, resentment, dominance, archetype, scene_context)
        result = predict_labels_from_artifact(model_path, features, feature_schema=_SUBTEXT_FEATURE_SCHEMA)
        if result.stub:
            ensure_stub_allowed("Drama subtext model stub fallback", allow_env="ALLOW_DRAMA_MODEL_STUB")
            _set_subtext_engine_placeholder(True)
            return None
        labels = list(result.labels)
        if not labels:
            _set_subtext_engine_placeholder(True)
            return None
        _set_subtext_engine_placeholder(False)
        return _labels_to_action(labels)
    except Exception as exc:  # noqa: BLE001
        _set_subtext_engine_placeholder(True)
        _logger.debug("SubtextEngine: model inference failed (%s); using rule-based path", exc)
        return None


class SubtextEngine:
    """Generates structured subtext suggestions for dialogue beats.

    When ``DRAMA_SUBTEXT_MODEL_PATH`` is configured, the engine uses a trained
    :class:`~sklearn.multioutput.MultiOutputClassifier` to predict 5 binary
    subtext labels which are mapped to a ``psychological_action``.  When no
    model is available the rule-based fallback is used.

    :data:`SUBTEXT_ENGINE_PLACEHOLDER` is ``True`` while the rule-based path
    is active; monitor via Prometheus metric ``subtext_engine_placeholder == 1``.
    """

    def infer_dialogue_actions(
        self,
        speaker_profile: Any,
        target_profile: Any,
        relationship_forward: Optional[Any],
        scene_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        scene_context = scene_context or {}

        trust = float(getattr(relationship_forward, "trust_level", 0.0) or 0.0) if relationship_forward else 0.0
        resentment = float(getattr(relationship_forward, "resentment_level", 0.0) or 0.0) if relationship_forward else 0.0
        dominance = float(getattr(relationship_forward, "dominance_source_over_target", 0.0) or 0.0) if relationship_forward else 0.0
        archetype = getattr(speaker_profile, "archetype", None)

        # Try ML model first; fall back to rules if unavailable.
        model_result = _try_model_subtext(trust, resentment, dominance, archetype, scene_context)
        if model_result is not None:
            act, hidden_intent = model_result
        else:
            act, hidden_intent = self._rule_based_action(trust, resentment, dominance, archetype)

        return {
            "speaker_id": str(speaker_profile.id),
            "target_id": str(target_profile.id),
            "psychological_action": act,
            "hidden_intent": hidden_intent,
            "suggested_subtext": getattr(speaker_profile, "mask_strategy", None)
            or "Conceal true stakes behind cleaner language",
            "threat_level": scene_context.get("exposure_risk", 0.3),
        }

    @staticmethod
    def _rule_based_action(
        trust: float,
        resentment: float,
        dominance: float,
        archetype: str | None,
    ) -> tuple[str, str]:
        """Original rule-based action selection — used when no model is configured."""
        if resentment > 0.6:
            return "attack", "Punish while maintaining plausible deniability"
        if dominance > 0.6:
            return "dominate", "Narrow the other character's perceived options"
        if trust > 0.6:
            return "reassure", "Stabilize alliance and preserve emotional access"
        if (archetype or "").lower() == "manipulator":
            return "redirect", "Change frame before accountability lands"
        return "probe", "Test the other character's position"
