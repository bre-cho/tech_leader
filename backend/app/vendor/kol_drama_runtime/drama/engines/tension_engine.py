from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional

from app.core.production_gate import ensure_stub_allowed
from app.drama.engines._model_path import get_drama_model_path

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model integration
# ---------------------------------------------------------------------------
# When DRAMA_TENSION_MODEL_PATH is set and points to a valid joblib/ONNX
# artifact, TensionEngine delegates to ml/serving.predict_from_artifact() instead of
# the heuristic formulas.  This path is prepared but not yet activated because
# no trained artifact exists — hence TENSION_ENGINE_PLACEHOLDER=True.
#
# To activate:
#   1. Train a drama-tension model (features → tension score ∈ [0, 100]).
#   2. Save it with: joblib.dump(model, "<path>/drama_tension_model.joblib")
#   3. Set DRAMA_TENSION_MODEL_PATH=<path>/drama_tension_model.joblib
#
# Monitor: Prometheus metric `tension_engine_placeholder` is 1 while the
# heuristic path is active so ops know the model has not yet been trained.
# ---------------------------------------------------------------------------

TENSION_ENGINE_PLACEHOLDER: bool = True  # flipped to False when a real model loads
# Lock protecting both writes AND reads of TENSION_ENGINE_PLACEHOLDER so
# that concurrent workers see a consistent value when the model first loads.
_PLACEHOLDER_LOCK: threading.Lock = threading.Lock()
_placeholder_state: dict[str, bool] = {"value": True}

_MODEL_PATH = os.environ.get("DRAMA_TENSION_MODEL_PATH", "").strip()


def _set_tension_engine_placeholder(value: bool) -> None:
    global TENSION_ENGINE_PLACEHOLDER
    with _PLACEHOLDER_LOCK:
        _placeholder_state["value"] = value
        TENSION_ENGINE_PLACEHOLDER = value


def is_tension_engine_placeholder() -> bool:
    """Return the current value of :data:`TENSION_ENGINE_PLACEHOLDER` under lock.

    Use this instead of reading the global directly when the caller needs a
    consistent snapshot (e.g. Prometheus metrics collection in a multi-worker
    environment).
    """
    with _PLACEHOLDER_LOCK:
        return _placeholder_state["value"]

# ---------------------------------------------------------------------------
# Heuristic fallback defaults — used when scene_context does not supply these
# keys.  All four values can be tuned via environment variables without a code
# deploy, e.g. for different genre defaults or content policies.
#
# DRAMA_TENSION_DEFAULT_EXPOSURE_RISK        (float, default 8.0, range [0, 10])
# DRAMA_TENSION_DEFAULT_UNRESOLVED_MEMORY    (float, default 6.0, range [0, 10])
# DRAMA_TENSION_DEFAULT_TIME_PRESSURE        (float, default 5.0, range [0, 10])
# DRAMA_TENSION_DEFAULT_SOCIAL_CONSEQUENCE   (float, default 6.0, range [0, 10])
# ---------------------------------------------------------------------------

def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


_DEFAULT_EXPOSURE_RISK = _env_float("DRAMA_TENSION_DEFAULT_EXPOSURE_RISK", 8.0)
_DEFAULT_UNRESOLVED_MEMORY = _env_float("DRAMA_TENSION_DEFAULT_UNRESOLVED_MEMORY", 6.0)
_DEFAULT_TIME_PRESSURE = _env_float("DRAMA_TENSION_DEFAULT_TIME_PRESSURE", 5.0)
_DEFAULT_SOCIAL_CONSEQUENCE = _env_float("DRAMA_TENSION_DEFAULT_SOCIAL_CONSEQUENCE", 6.0)


_TENSION_FEATURE_SCHEMA = [
    "intent_count",
    "relationship_count",
    "hidden_agenda_sum",
    "dominance_sum",
    "exposure_risk",
    "unresolved_prior_memory",
    "time_pressure",
    "social_consequence",
]


def _try_model_score(features: Dict[str, Any]) -> float | None:
    """Attempt inference via ml/serving if a model artifact is configured.

    Returns a normalised score in [0, 100], or ``None`` when no model is
    configured or inference fails.  Failure is non-fatal; the heuristic
    fallback is used instead and the global placeholder flag stays True.
    """
    model_path = get_drama_model_path("DRAMA_TENSION_MODEL_PATH") or _MODEL_PATH
    if not model_path:
        _set_tension_engine_placeholder(True)
        return None
    try:
        from app.ml.serving import predict_from_artifact  # noqa: PLC0415
        result = predict_from_artifact(model_path, features, feature_schema=_TENSION_FEATURE_SCHEMA)
        if result.stub:
            ensure_stub_allowed("Drama tension model stub fallback", allow_env="ALLOW_DRAMA_MODEL_STUB")
            _set_tension_engine_placeholder(True)
            return None
        raw = float(result.score)
        # ml/serving returns scores ∈ [0, 1]; scale to [0, 100] for compatibility.
        _set_tension_engine_placeholder(False)
        return round(max(0.0, min(raw * 100.0, 100.0)), 2)
    except Exception as exc:  # noqa: BLE001
        _set_tension_engine_placeholder(True)
        _logger.debug("TensionEngine: model inference failed (%s); using heuristic", exc)
        return None


@dataclass
class TensionScoreBreakdown:
    goal_collision: float
    hidden_agenda_asymmetry: float
    emotional_exposure_risk: float
    power_imbalance: float
    unresolved_prior_memory: float
    time_pressure: float
    social_consequence: float

    @property
    def total(self) -> float:
        total = round(
            self.goal_collision
            + self.hidden_agenda_asymmetry
            + self.emotional_exposure_risk
            + self.power_imbalance
            + self.unresolved_prior_memory
            + self.time_pressure
            + self.social_consequence,
            2,
        )
        return max(0.0, min(total, 100.0))


class TensionEngine:
    """Computes scene-level tension from intent, relationships, and beat context.

    When ``DRAMA_TENSION_MODEL_PATH`` points to a trained joblib artifact the
    score is computed by the ML model via ``ml/serving.predict_from_artifact()``.
    Otherwise, heuristic formulas are used and
    :data:`TENSION_ENGINE_PLACEHOLDER` stays ``True`` to signal that a real
    model should be trained and registered.

    Monitor via Prometheus: ``tension_engine_placeholder == 1`` means only
    heuristic scores are being produced.
    """

    def score(
        self,
        intents: List[Any],
        relationship_snapshots: Iterable[Any],
        scene_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        scene_context = scene_context or {}
        relationships = list(relationship_snapshots)

        # Attempt model-based score first.
        features = {
            "intent_count": float(len(intents)),
            "relationship_count": float(len(relationships)),
            "hidden_agenda_sum": float(sum(getattr(r, "hidden_agenda_score", 0.0) for r in relationships)),
            "dominance_sum": float(sum(abs(getattr(r, "dominance_source_over_target", 0.0)) for r in relationships)),
            "exposure_risk": float(scene_context.get("exposure_risk", _DEFAULT_EXPOSURE_RISK)),
            "unresolved_prior_memory": float(scene_context.get("unresolved_prior_memory", _DEFAULT_UNRESOLVED_MEMORY)),
            "time_pressure": float(scene_context.get("time_pressure", _DEFAULT_TIME_PRESSURE)),
            "social_consequence": float(scene_context.get("social_consequence", _DEFAULT_SOCIAL_CONSEQUENCE)),
        }
        model_score = _try_model_score(features)
        if model_score is not None:
            return {
                "tension_score": model_score,
                "breakdown": features,
                "flat_scene": model_score < 35.0,
                "source": "model",
            }

        # Heuristic fallback — placeholder until a model is trained.
        _logger.debug(
            "TensionEngine: PLACEHOLDER heuristic active (tension_engine_placeholder=1). "
            "Train a drama-tension model and set DRAMA_TENSION_MODEL_PATH to activate the ML path."
        )
        goal_collision = min(len(intents) * 8.0, 20.0)
        hidden_agenda_asymmetry = min(sum(getattr(r, "hidden_agenda_score", 0.0) for r in relationships) * 0.5, 15.0)
        emotional_exposure_risk = float(scene_context.get("exposure_risk", _DEFAULT_EXPOSURE_RISK))
        power_imbalance = min(sum(abs(getattr(r, "dominance_source_over_target", 0.0)) for r in relationships) * 0.4, 15.0)
        unresolved_prior_memory = float(scene_context.get("unresolved_prior_memory", _DEFAULT_UNRESOLVED_MEMORY))
        time_pressure = float(scene_context.get("time_pressure", _DEFAULT_TIME_PRESSURE))
        social_consequence = float(scene_context.get("social_consequence", _DEFAULT_SOCIAL_CONSEQUENCE))

        breakdown = TensionScoreBreakdown(
            goal_collision=goal_collision,
            hidden_agenda_asymmetry=hidden_agenda_asymmetry,
            emotional_exposure_risk=emotional_exposure_risk,
            power_imbalance=power_imbalance,
            unresolved_prior_memory=unresolved_prior_memory,
            time_pressure=time_pressure,
            social_consequence=social_consequence,
        )

        return {
            "tension_score": breakdown.total,
            "breakdown": asdict(breakdown),
            "flat_scene": breakdown.total < 35.0,
            "source": "heuristic_placeholder",
        }
