from __future__ import annotations

import logging
import os
import re
import threading
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from app.core.production_gate import ensure_stub_allowed
from app.drama.engines._model_path import get_drama_model_path

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Placeholder flag
# ---------------------------------------------------------------------------
# MemoryRecallEngine uses heuristic scoring (trigger-text matching +
# persistence/emotional weights) when no trained model is available.
#
# To activate a real model:
#   1. Train a recall-relevance model via ml/training/drama_memory_recall_trainer.py.
#   2. Save it with: joblib.dump(model, "<path>/memory_recall_model.joblib")
#   3. Set DRAMA_MEMORY_RECALL_MODEL_PATH=<path>/memory_recall_model.joblib
#
# Monitor: Prometheus metric `memory_recall_engine_placeholder` is 1 while the
# heuristic path is active so ops know a real model has not yet been deployed.
# ---------------------------------------------------------------------------

MEMORY_RECALL_ENGINE_PLACEHOLDER: bool = True  # flipped to False when a real model loads
# Lock protecting both writes AND reads of MEMORY_RECALL_ENGINE_PLACEHOLDER so
# that concurrent workers see a consistent value when the model first loads.
_PLACEHOLDER_LOCK: threading.Lock = threading.Lock()
_placeholder_state: dict[str, bool] = {"value": True}

_MODEL_PATH = os.environ.get("DRAMA_MEMORY_RECALL_MODEL_PATH", "").strip()


def _set_memory_recall_engine_placeholder(value: bool) -> None:
    global MEMORY_RECALL_ENGINE_PLACEHOLDER
    with _PLACEHOLDER_LOCK:
        _placeholder_state["value"] = value
        MEMORY_RECALL_ENGINE_PLACEHOLDER = value


def is_memory_recall_engine_placeholder() -> bool:
    """Return the current value of :data:`MEMORY_RECALL_ENGINE_PLACEHOLDER` under lock.

    Use this instead of reading the global directly when the caller needs a
    consistent snapshot (e.g. Prometheus metrics collection in a multi-worker
    environment).
    """
    with _PLACEHOLDER_LOCK:
        return _placeholder_state["value"]


_MEMORY_RECALL_FEATURE_SCHEMA = [
    "trigger_in_recall",
    "trigger_in_meaning",
    "persistence_score",
    "emotional_weight",
    "trigger_len_norm",
]


def _try_model_recall(memory: object, trigger: str) -> float | None:
    """Attempt to score (trigger, memory) relevance using the trained model.

    Returns a relevance score in [0, 1], or ``None`` when no model is
    configured or inference fails.  Failure is non-fatal; the heuristic
    fallback is used instead and the global placeholder flag stays True.

    Feature vector matches the drama_memory_recall_trainer schema:
      [trigger_in_recall, trigger_in_meaning, persistence_score,
       emotional_weight, trigger_len_norm]
    """
    model_path = get_drama_model_path("DRAMA_MEMORY_RECALL_MODEL_PATH") or _MODEL_PATH
    if not model_path:
        _set_memory_recall_engine_placeholder(True)
        return None
    try:
        from app.ml.serving import predict_from_artifact  # noqa: PLC0415

        recall_trigger = (getattr(memory, "recall_trigger", "") or "").lower()
        meaning_label = (getattr(memory, "meaning_label", "") or "").lower()
        persistence_score = float(getattr(memory, "persistence_score", 0.0) or 0.0)
        emotional_weight = min(float(getattr(memory, "emotional_weight", 0.0) or 0.0), 1.0)

        features = {
            "trigger_in_recall": _trigger_match_score(trigger, recall_trigger),
            "trigger_in_meaning": _trigger_match_score(trigger, meaning_label),
            "persistence_score": persistence_score,
            "emotional_weight": emotional_weight,
            "trigger_len_norm": min(len(trigger) / 50.0, 1.0),
        }
        result = predict_from_artifact(model_path, features, feature_schema=_MEMORY_RECALL_FEATURE_SCHEMA)
        if result.stub:
            ensure_stub_allowed("Drama memory recall model stub fallback", allow_env="ALLOW_DRAMA_MODEL_STUB")
            _set_memory_recall_engine_placeholder(True)
            return None
        _set_memory_recall_engine_placeholder(False)
        return max(0.0, min(1.0, float(result.score)))
    except Exception as exc:  # noqa: BLE001
        _set_memory_recall_engine_placeholder(True)
        _logger.debug("MemoryRecallEngine: model inference failed (%s); using heuristic", exc)
        return None


@dataclass
class RecallCandidate:
    memory: object
    score: float


def _trigger_match_score(trigger: str, text: str) -> float:
    """Return a match score in [0, 1] for *trigger* inside *text*.

    Uses word-boundary matching (``\\b``) so short triggers like ``"war"``
    do not spuriously match substrings such as ``"forward"`` or ``"warden"``.
    Returns 1.0 on a full word-boundary match, 0.5 on a substring-only match
    (fallback for multi-word phrases that may span word boundaries), and 0.0
    when neither matches.  Both *trigger* and *text* are expected to be
    already normalised to lower-case by the caller.
    """
    if not trigger:
        return 0.0
    # Escape regex metacharacters in the trigger so arbitrary text is safe.
    escaped = re.escape(trigger)
    if re.search(rf"\b{escaped}\b", text):
        return 1.0
    # Substring fallback for multi-word triggers or languages without clear
    # word boundaries (e.g. CJK).  Slightly lower weight so word-boundary
    # matches are preferred when both are possible.
    if trigger in text:
        return 0.5
    return 0.0


class MemoryRecallEngine:
    """Ranks stored drama memories for a given trigger.

    Current implementation is heuristic and intentionally simple so the
    persistence / API layer can stabilize before a learned retrieval model is
    used.  :data:`MEMORY_RECALL_ENGINE_PLACEHOLDER` is ``True`` while this
    heuristic path is active; monitor via Prometheus metric
    ``memory_recall_engine_placeholder == 1``.

    Trigger matching uses word-boundary regular expressions (``\\b``) so short
    triggers such as ``"war"`` do not falsely match substrings like
    ``"forward"``.  Multi-word triggers still fall back to substring matching
    with a reduced score weight (0.5 ×) so they are ranked below exact
    word-boundary matches.
    """

    TRIGGER_BOOST_WEIGHT = 0.45
    PERSISTENCE_WEIGHT = 0.35
    EMOTIONAL_WEIGHT = 0.20

    def recall(self, memories: Sequence[object], trigger: str, limit: int = 10) -> List[object]:
        normalized_trigger = (trigger or "").strip().lower()
        scored: List[RecallCandidate] = []
        for memory in memories:
            score = self._score_memory(memory, normalized_trigger)
            scored.append(RecallCandidate(memory=memory, score=score))

        scored.sort(key=lambda item: item.score, reverse=True)
        return [item.memory for item in scored[:limit]]

    def _score_memory(self, memory: object, trigger: str) -> float:
        # Attempt model-based relevance score first.
        model_score = _try_model_recall(memory, trigger)
        if model_score is not None:
            return model_score

        # Heuristic fallback — used until a model is trained and configured.
        recall_trigger = getattr(memory, "recall_trigger", "") or ""
        meaning_label = getattr(memory, "meaning_label", "") or ""
        persistence_score = float(getattr(memory, "persistence_score", 0.0) or 0.0)
        emotional_weight = float(getattr(memory, "emotional_weight", 0.0) or 0.0)

        text = f"{recall_trigger} {meaning_label}".lower()
        # Use word-boundary matching to avoid false positives with short
        # triggers (e.g. "war" matching "forward").
        trigger_match = _trigger_match_score(trigger, text)

        return (
            trigger_match * self.TRIGGER_BOOST_WEIGHT
            + persistence_score * self.PERSISTENCE_WEIGHT
            + min(emotional_weight, 1.0) * self.EMOTIONAL_WEIGHT
        )
