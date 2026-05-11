from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List

from .capability_router import CapabilityRouter
from .contracts import MultiModalVideoIntent, ProviderCapability, ProviderDecision
from .learning_loop import LearningLoopStore

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@dataclass
class ScoringWeights:
    """Weights for the provider scoring formula.

    These are kept in a single dataclass so A/B test variants can supply
    different weights without forking the scoring code.  The default values
    preserve the original behaviour (quality 50%, latency 15%, cost 15%,
    the remaining 20% come from contextual bonuses).

    All weight attributes should be non-negative.  The formula is:
        total = quality * w_quality
              + latency * w_latency
              + cost    * w_cost
              + reference_bonus * w_reference_bonus
              + audio_bonus     * w_audio_bonus
              + edit_bonus      * w_edit_bonus
              + learning_bonus  (unscaled, capped by LearningLoopStore)

    **Score range note (P13):**
    The primary weights (``w_quality + w_latency + w_cost = 0.80``) and the
    contextual bonus fields sum to a theoretical maximum of
    ``0.80 + 0.08 + 0.05 + 0.05 + 0.06 = 1.04`` before the learning bonus.
    In practice the learning bonus is bounded to roughly ±0.30 by
    :class:`~app.video_engine.brain.learning_loop.LearningLoopStore`, so the
    final score can exceed 1.0 when all bonuses are active.  The
    :meth:`~ProviderDecisionEngine._score` method **clamps the total to
    [0.0, 1.0]** before returning so downstream consumers (e.g.
    ``decide_visual_engine_route``) always receive a normalised confidence
    value.  The raw per-component breakdown is still reported in the
    scorecard dict for debugging.
    """

    w_quality: float = 0.50
    w_latency: float = 0.15
    w_cost: float = 0.15
    # Contextual bonuses (applied as full additive terms, not scaled)
    reference_image_video_bonus: float = 0.08
    reference_audio_bonus: float = 0.05
    audio_bonus: float = 0.05
    edit_bonus: float = 0.06


# Default weights — can be overridden per-engine-instance for experiments.
DEFAULT_SCORING_WEIGHTS = ScoringWeights()


@dataclass
class ScoringNormalization:
    """Normalization ceilings for latency and cost scoring.

    These constants convert raw provider metrics into [0, 1] scores before
    the weighted formula is applied.  Override via
    ``SCORING_NORMALIZATION=<JSON>`` env var (same profile-keyed mechanism as
    :data:`ScoringWeights`) to tune without code changes.

    Attributes
    ----------
    max_latency_ms:
        Latency ceiling in milliseconds.  Providers at or above this value
        score 0.0 for latency; providers at 0 ms score 1.0.  Default: 180 s.
    max_cost_per_run_usd:
        Cost ceiling in USD for the full render duration.  Providers at or
        above this value score 0.0 for cost.  Default: $1.00.
    """

    max_latency_ms: float = 180_000.0
    max_cost_per_run_usd: float = 1.0


DEFAULT_SCORING_NORMALIZATION = ScoringNormalization()

# ---------------------------------------------------------------------------
# Parse error counters — incremented when env var JSON is malformed.
# Exposed as Prometheus metrics via collect_scoring_parse_error_metrics().
#
# P7: The in-process counters reset to 0 on every worker restart which makes
# them misleading in multi-process/rolling-restart environments.  A Redis
# INCR key is also updated (when Redis is available) so the cross-process
# total persists across restarts, mirroring the pattern used by
# distribution/performance_tracker.py for stub-return tracking.
# ---------------------------------------------------------------------------
scoring_weights_parse_errors: int = 0
scoring_normalization_parse_errors: int = 0

_REDIS_SCORING_WEIGHTS_ERROR_KEY = "scoring:weights_parse_error_total"
_REDIS_SCORING_NORMALIZATION_ERROR_KEY = "scoring:normalization_parse_error_total"


def _incr_scoring_error_counter(redis_key: str) -> None:
    """Increment the cross-process Redis counter for a scoring parse error.

    Falls back silently when Redis is unavailable; the in-process counter
    still tracks errors for the current worker's Prometheus scrape.
    Uses the process-wide shared client from :mod:`app.core.redis`.
    """
    from app.core.redis import get_shared_redis_client, reset_shared_redis_client  # noqa: PLC0415

    r = get_shared_redis_client()
    if r is None:
        return
    try:
        r.incr(redis_key)
    except Exception:  # noqa: BLE001
        # Redis became unavailable — reset the shared client so the next call
        # attempts a fresh connection rather than failing permanently.
        reset_shared_redis_client()


def _get_scoring_counter_redis(redis_key: str) -> int | None:
    """Return the cross-process scoring counter from Redis for *redis_key*, or ``None``."""
    from app.core.redis import get_shared_redis_client, reset_shared_redis_client  # noqa: PLC0415

    r = get_shared_redis_client()
    if r is None:
        return None
    try:
        raw = r.get(redis_key)
        return int(raw) if raw is not None else None
    except Exception:  # noqa: BLE001
        reset_shared_redis_client()
        return None


def get_scoring_weights_parse_error_counter_redis() -> int | None:
    """Return the cross-process weights parse-error count from Redis, or ``None``."""
    return _get_scoring_counter_redis(_REDIS_SCORING_WEIGHTS_ERROR_KEY)


def get_scoring_normalization_parse_error_counter_redis() -> int | None:
    """Return the cross-process normalization parse-error count from Redis, or ``None``."""
    return _get_scoring_counter_redis(_REDIS_SCORING_NORMALIZATION_ERROR_KEY)


def load_scoring_normalization() -> ScoringNormalization:
    """Load scoring normalization ceilings from ``SCORING_NORMALIZATION`` env var.

    The env var should contain a JSON object with any subset of
    :class:`ScoringNormalization` field names, e.g.::

        SCORING_NORMALIZATION='{"max_latency_ms": 120000, "max_cost_per_run_usd": 0.5}'

    Falls back to :data:`DEFAULT_SCORING_NORMALIZATION` when no override is
    found or the JSON is malformed.
    """
    import json as _json  # noqa: PLC0415
    import os  # noqa: PLC0415

    raw = os.getenv("SCORING_NORMALIZATION", "").strip()
    if raw:
        try:
            overrides = _json.loads(raw)
            if isinstance(overrides, dict):
                import dataclasses  # noqa: PLC0415
                base = dataclasses.asdict(DEFAULT_SCORING_NORMALIZATION)
                base.update({k: float(v) for k, v in overrides.items() if k in base})
                candidate = ScoringNormalization(**base)
                return _validate_scoring_normalization(candidate, "SCORING_NORMALIZATION")
        except Exception as _exc:  # noqa: BLE001
            import logging as _logging  # noqa: PLC0415
            global scoring_normalization_parse_errors
            scoring_normalization_parse_errors += 1
            _incr_scoring_error_counter(_REDIS_SCORING_NORMALIZATION_ERROR_KEY)
            _logging.getLogger(__name__).warning(
                "load_scoring_normalization: invalid JSON in SCORING_NORMALIZATION "
                "(%s: %s); using default normalization ceilings",
                type(_exc).__name__,
                _exc,
            )
    return DEFAULT_SCORING_NORMALIZATION

def load_scoring_weights(routing_profile: str | None = None) -> ScoringWeights:
    """Load scoring weights for *routing_profile* from environment variables.

    This enables A/B weight experiments without code changes or DB migrations.
    Set ``SCORING_WEIGHTS_<PROFILE>=<JSON>`` (upper-cased profile name) to
    override weights for a specific profile.  The JSON object may contain any
    subset of :class:`ScoringWeights` field names.

    Example::

        SCORING_WEIGHTS_SOCIAL_FAST='{"w_quality": 0.40, "w_latency": 0.25}'

    Falls back to :data:`DEFAULT_SCORING_WEIGHTS` when no override is found
    or the JSON is malformed.

    Parameters
    ----------
    routing_profile:
        The routing profile name (e.g. ``"social_fast"``).  ``None`` or empty
        uses the global default.
    """
    import json as _json  # noqa: PLC0415
    import os  # noqa: PLC0415

    if routing_profile:
        env_key = f"SCORING_WEIGHTS_{routing_profile.upper()}"
        raw = os.getenv(env_key, "").strip()
        if raw:
            try:
                overrides = _json.loads(raw)
                if isinstance(overrides, dict):
                    import dataclasses  # noqa: PLC0415
                    base = dataclasses.asdict(DEFAULT_SCORING_WEIGHTS)
                    base.update({k: float(v) for k, v in overrides.items() if k in base})
                    candidate = ScoringWeights(**base)
                    return _validate_scoring_weights(candidate, env_key)
            except Exception as _exc:  # noqa: BLE001
                import logging as _logging  # noqa: PLC0415
                global scoring_weights_parse_errors
                scoring_weights_parse_errors += 1
                _incr_scoring_error_counter(_REDIS_SCORING_WEIGHTS_ERROR_KEY)
                _logging.getLogger(__name__).warning(
                    "load_scoring_weights: invalid JSON in %s (%s: %s); using default weights",
                    env_key,
                    type(_exc).__name__,
                    _exc,
                )
    return DEFAULT_SCORING_WEIGHTS

def _validate_scoring_normalization(norm: ScoringNormalization, source: str) -> ScoringNormalization:
    """Validate that normalization ceilings are strictly positive.

    Returns the supplied *norm* unchanged if valid.  Resets out-of-range
    fields to their defaults and logs a warning so operators know which
    env var to fix.
    """
    import dataclasses as _dc  # noqa: PLC0415
    import logging as _logging  # noqa: PLC0415

    _log = _logging.getLogger(__name__)
    base = _dc.asdict(DEFAULT_SCORING_NORMALIZATION)
    current = _dc.asdict(norm)
    fixed: dict = {}
    for field_name, default_val in base.items():
        val = current.get(field_name, default_val)
        if not isinstance(val, (int, float)) or val <= 0:
            _log.warning(
                "%s: %s=%r is invalid (must be > 0); resetting to default %r",
                source,
                field_name,
                val,
                default_val,
            )
            fixed[field_name] = default_val
        else:
            fixed[field_name] = val
    return ScoringNormalization(**fixed)


def _validate_scoring_weights(weights: ScoringWeights, source: str) -> ScoringWeights:
    """Validate that scoring weights are non-negative.

    The primary weight fields (``w_quality``, ``w_latency``, ``w_cost``) are
    also clamped to [0, 1].  Bonus fields are clamped to [0, 1].  Out-of-range
    values are reset to their defaults and a warning is logged.
    """
    import dataclasses as _dc  # noqa: PLC0415
    import logging as _logging  # noqa: PLC0415

    _log = _logging.getLogger(__name__)
    base = _dc.asdict(DEFAULT_SCORING_WEIGHTS)
    current = _dc.asdict(weights)
    fixed: dict = {}
    for field_name, default_val in base.items():
        val = current.get(field_name, default_val)
        if not isinstance(val, (int, float)) or val < 0:
            _log.warning(
                "%s: %s=%r is invalid (must be >= 0); resetting to default %r",
                source,
                field_name,
                val,
                default_val,
            )
            fixed[field_name] = default_val
        else:
            # Clamp each weight to [0, 1] — values above 1 make no physical
            # sense for a normalized scoring formula and are almost certainly
            # a misconfiguration.
            if val > 1.0:
                _log.warning(
                    "%s: %s=%r exceeds 1.0; clamping to 1.0",
                    source,
                    field_name,
                    val,
                )
                val = 1.0
            fixed[field_name] = val
    return ScoringWeights(**fixed)


class NoEligibleProviderError(ValueError):
    """Raised when no registered provider can satisfy the given intent.

    Callers should inspect the ``rejected`` attribute to understand why each
    candidate provider was excluded before deciding how to handle the failure
    (e.g. relaxing constraints, returning a user-facing error, or logging).
    """

    def __init__(self, message: str, rejected: List[Dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.rejected: List[Dict[str, Any]] = rejected or []


class ProviderDecisionEngine:
    def __init__(
        self,
        capability_router: CapabilityRouter | None = None,
        learning_store: LearningLoopStore | None = None,
        scoring_weights: ScoringWeights | None = None,
        scoring_normalization: ScoringNormalization | None = None,
        db: "Session | None" = None,
    ):
        self.capability_router = capability_router or CapabilityRouter()
        # db is forwarded to LearningLoopStore so the DB backend is used in
        # production.  When db is None in production a _NoOpBackend is used
        # (learning signals are dropped but the engine never crashes).
        self.learning_store = learning_store or LearningLoopStore(db=db)
        self.scoring_weights = scoring_weights or DEFAULT_SCORING_WEIGHTS
        self.scoring_normalization = scoring_normalization or load_scoring_normalization()

    def decide(self, intent: MultiModalVideoIntent, requested_provider: str = "auto", routing_profile: str = "cinematic_ads") -> ProviderDecision:
        chain = self.capability_router.candidate_chain(routing_profile, requested_provider)
        eligible, rejected = self.capability_router.evaluate(intent, chain)
        if not eligible:
            raise NoEligibleProviderError(
                f"No eligible provider for intent (mode={intent.mode.value}, "
                f"aspect_ratio={intent.aspect_ratio}, duration={intent.duration_seconds}s). "
                f"rejected={rejected}",
                rejected=rejected,
            )

        # Use per-profile scoring weights when an env-var override is present;
        # fall back to the instance-level weights (set at construction time).
        profile_weights = load_scoring_weights(routing_profile)
        # Instance-level weights take precedence when explicitly supplied (e.g.
        # in tests or A/B experiments that construct the engine with custom weights).
        effective_weights = (
            self.scoring_weights
            if self.scoring_weights is not DEFAULT_SCORING_WEIGHTS
            else profile_weights
        )

        scored = []
        for cap in eligible:
            score, detail = self._score(cap, intent, routing_profile, weights=effective_weights, normalization=self.scoring_normalization)
            scored.append((score, cap, detail))
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_cap, best_detail = scored[0]
        fallback_chain = [cap.provider for _, cap, _ in scored]
        return ProviderDecision(
            selected_provider=best_cap.provider,
            selected_model=self._select_model(best_cap, intent),
            decision_reason=best_detail["reason"],
            fallback_chain=fallback_chain,
            rejected=rejected,
            scorecard={cap.provider: detail | {"total": round(score, 4)} for score, cap, detail in scored},
        )

    def _score(
        self,
        cap: ProviderCapability,
        intent: MultiModalVideoIntent,
        routing_profile: str,
        weights: ScoringWeights | None = None,
        normalization: ScoringNormalization | None = None,
    ) -> tuple[float, Dict[str, Any]]:
        w = weights if weights is not None else self.scoring_weights
        n = normalization if normalization is not None else self.scoring_normalization
        quality = cap.quality_bias
        latency = max(0.0, min(1.0, 1.0 - cap.estimated_latency_ms / n.max_latency_ms))
        cost = max(0.0, min(1.0, 1.0 - (cap.estimated_cost_per_second * intent.duration_seconds) / n.max_cost_per_run_usd))
        reference_bonus = 0.0
        if intent.references:
            if cap.supports_image_reference or cap.supports_video_reference:
                reference_bonus += w.reference_image_video_bonus
            if any(r.kind == "audio" for r in intent.references) and cap.supports_audio_reference:
                reference_bonus += w.reference_audio_bonus
        audio_bonus = w.audio_bonus if intent.audio and cap.supports_audio else 0.0
        edit_bonus = w.edit_bonus if intent.mode.value in {"video_edit", "video_extend"} and (cap.supports_video_editing or cap.supports_video_extension) else 0.0
        learning_bonus = self.learning_store.provider_bonus(routing_profile, cap.provider)
        total = (
            quality * w.w_quality
            + latency * w.w_latency
            + cost * w.w_cost
            + reference_bonus
            + audio_bonus
            + edit_bonus
            + learning_bonus
        )
        # Clamp to [0.0, 1.0] so callers always receive a normalised confidence
        # value.  The theoretical maximum with all bonuses and a perfect learning
        # history slightly exceeds 1.0 (see ScoringWeights docstring).
        total = max(0.0, min(1.0, total))
        reason = "best weighted score for quality, constraints, cost, latency, references, and learning history"
        return total, {
            "quality": round(quality, 4),
            "latency": round(latency, 4),
            "cost": round(cost, 4),
            "reference_bonus": round(reference_bonus, 4),
            "audio_bonus": round(audio_bonus, 4),
            "edit_bonus": round(edit_bonus, 4),
            "learning_bonus": round(learning_bonus, 4),
            "reason": reason,
        }

    def _select_model(self, cap: ProviderCapability, intent: MultiModalVideoIntent) -> str | None:
        if not cap.models:
            return None
        if intent.quality_tier == "draft":
            # Prefer the explicitly declared draft model over a name-based heuristic.
            if cap.draft_model and cap.draft_model in cap.models:
                return cap.draft_model
            # Legacy fallback: look for a model whose name contains "fast".
            # This heuristic is kept for providers that haven't yet declared
            # draft_model; set ProviderCapability.draft_model to remove the need.
            fast = [m for m in cap.models if "fast" in m.lower()]
            return fast[0] if fast else cap.models[-1]
        return cap.models[0]
