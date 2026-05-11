from __future__ import annotations

import json as _json
import logging as _logging
import os as _os
from typing import Dict

from .contracts import ProviderCapability

_logger = _logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Runtime capability overrides
# ---------------------------------------------------------------------------
# Set CAPABILITY_OVERRIDES='{"veo": {"quality_bias": 0.90, "estimated_latency_ms": 55000}}'
# to tune numeric provider capability fields without a code deploy.
# Only fields that already exist on ProviderCapability and have numeric or
# boolean types may be overridden; unknown keys are silently skipped.

_CAPABILITY_NUMERIC_FIELDS = frozenset(
    {
        "quality_bias",
        "estimated_cost_per_second",
        "estimated_latency_ms",
        "max_duration_seconds",
    }
)

_CAPABILITY_BOOL_FIELDS = frozenset(
    {
        "supports_audio",
        "supports_image_reference",
        "supports_video_reference",
        "supports_audio_reference",
        "supports_video_editing",
        "supports_video_extension",
        "supports_text_overlay",
    }
)


def _load_capability_overrides() -> Dict[str, Dict[str, object]]:
    """Parse ``CAPABILITY_OVERRIDES`` env var into a nested override dict.

    Example::

        CAPABILITY_OVERRIDES='{"veo": {"quality_bias": 0.90}, "kling": {"estimated_latency_ms": 50000}}'

    Returns an empty dict when the env var is absent or malformed.  Unknown
    provider names and unknown field names are silently skipped so a typo
    never silently degrades routing — the original capability is used instead
    and a WARNING is emitted.
    """
    raw = _os.getenv("CAPABILITY_OVERRIDES", "").strip()
    if not raw:
        return {}
    try:
        parsed = _json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("expected a JSON object")
        return parsed  # type: ignore[return-value]
    except Exception as exc:  # noqa: BLE001
        _logger.warning(
            "_load_capability_overrides: invalid JSON in CAPABILITY_OVERRIDES "
            "(%s: %s); no capability overrides applied.",
            type(exc).__name__,
            exc,
        )
        return {}


def _apply_capability_overrides(
    caps: Dict[str, ProviderCapability],
    overrides: Dict[str, Dict[str, object]],
) -> Dict[str, ProviderCapability]:
    """Return a copy of *caps* with provider fields patched by *overrides*.

    Only numeric fields listed in ``_CAPABILITY_NUMERIC_FIELDS`` and boolean
    fields in ``_CAPABILITY_BOOL_FIELDS`` may be overridden.  Structural fields
    (``provider``, ``models``, ``modes``, ``aspect_ratios``) are intentionally
    excluded to prevent misconfiguration from silently breaking routing.
    """
    if not overrides:
        return caps
    result = dict(caps)
    for provider, field_overrides in overrides.items():
        if not isinstance(field_overrides, dict):
            _logger.warning(
                "_apply_capability_overrides: overrides for provider %r must be a dict; skipping.",
                provider,
            )
            continue
        cap = result.get(provider)
        if cap is None:
            _logger.warning(
                "_apply_capability_overrides: provider %r not found in capability registry; skipping.",
                provider,
            )
            continue
        kwargs: Dict[str, object] = {}
        for field, value in field_overrides.items():
            if field in _CAPABILITY_NUMERIC_FIELDS:
                try:
                    kwargs[field] = float(value)  # type: ignore[arg-type]
                except (TypeError, ValueError):
                    _logger.warning(
                        "_apply_capability_overrides: cannot cast %r=%r to float for provider %r; skipping field.",
                        field,
                        value,
                        provider,
                    )
            elif field in _CAPABILITY_BOOL_FIELDS:
                kwargs[field] = bool(value)
            else:
                _logger.warning(
                    "_apply_capability_overrides: field %r is not overridable for provider %r; skipping.",
                    field,
                    provider,
                )
        if kwargs:
            result[provider] = cap.model_copy(update=kwargs)
    return result


_LOCAL_STUB_CAPABILITY = ProviderCapability(
    provider="local_stub",
    models=["local-stub-video"],
    modes=["text_to_video", "image_to_video", "video_to_video", "reference_to_video", "video_edit", "video_extend"],
    aspect_ratios=["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"],
    max_duration_seconds=60,
    supports_audio=True,
    supports_image_reference=True,
    supports_video_reference=True,
    supports_audio_reference=True,
    supports_video_editing=True,
    supports_video_extension=True,
    supports_text_overlay=True,
    estimated_cost_per_second=0.0,
    estimated_latency_ms=1000,
    quality_bias=0.2,
)


def default_capabilities() -> Dict[str, ProviderCapability]:
    caps: Dict[str, ProviderCapability] = {
        "seedance": ProviderCapability(
            provider="seedance",
            models=["seedance-2.0", "seedance-2.0-fast"],
            modes=["text_to_video", "image_to_video", "video_to_video", "reference_to_video", "video_edit", "video_extend"],
            aspect_ratios=["16:9", "9:16", "4:3", "3:4", "21:9", "1:1"],
            max_duration_seconds=15,
            supports_audio=True,
            supports_image_reference=True,
            supports_video_reference=True,
            supports_audio_reference=True,
            supports_video_editing=True,
            supports_video_extension=True,
            supports_text_overlay=True,
            estimated_cost_per_second=0.010,
            estimated_latency_ms=45000,
            quality_bias=0.86,
        ),
        "veo": ProviderCapability(
            provider="veo",
            models=["veo-3", "veo-3.1", "veo-3.1-fast"],
            modes=["text_to_video", "image_to_video", "video_to_video"],
            aspect_ratios=["16:9", "9:16", "1:1"],
            max_duration_seconds=8,
            supports_audio=True,
            supports_image_reference=True,
            supports_video_reference=False,
            supports_audio_reference=False,
            estimated_cost_per_second=0.020,
            estimated_latency_ms=60000,
            quality_bias=0.88,
        ),
        "runway": ProviderCapability(
            provider="runway",
            models=["gen-4", "gen-3-alpha"],
            modes=["text_to_video", "image_to_video", "video_to_video", "video_edit"],
            aspect_ratios=["16:9", "9:16", "1:1", "4:3", "3:4"],
            max_duration_seconds=10,
            supports_audio=False,
            supports_image_reference=True,
            supports_video_reference=True,
            supports_video_editing=True,
            estimated_cost_per_second=0.015,
            estimated_latency_ms=50000,
            quality_bias=0.82,
        ),
        "kling": ProviderCapability(
            provider="kling",
            models=["kling-1.6", "kling-2.0"],
            modes=["text_to_video", "image_to_video", "video_to_video"],
            aspect_ratios=["16:9", "9:16", "1:1"],
            max_duration_seconds=10,
            supports_audio=False,
            supports_image_reference=True,
            supports_video_reference=True,
            estimated_cost_per_second=0.012,
            estimated_latency_ms=55000,
            quality_bias=0.78,
        ),
        "seedance2": ProviderCapability(
            provider="seedance2",
            models=["seedance2-1.0", "seedance2-1.0-fast"],
            modes=["text_to_video", "image_to_video", "reference_to_video"],
            aspect_ratios=["9:16", "16:9", "1:1"],
            max_duration_seconds=10,
            supports_audio=True,
            supports_image_reference=True,
            supports_video_reference=False,
            supports_audio_reference=False,
            supports_video_editing=False,
            supports_video_extension=False,
            supports_text_overlay=True,
            estimated_cost_per_second=0.009,
            estimated_latency_ms=35000,
            quality_bias=0.82,
        ),
    }

    # local_stub is available in non-production-like environments only.
    # In production/staging it is excluded so the routing table never
    # silently falls back to a fake provider that generates invalid URLs.
    from app.core.production_gate import is_production_or_staging  # noqa: PLC0415
    if not is_production_or_staging():
        caps["local_stub"] = _LOCAL_STUB_CAPABILITY

    # Apply runtime overrides from CAPABILITY_OVERRIDES env var so ops can
    # tune quality_bias / latency / cost without a code deploy.
    caps = _apply_capability_overrides(caps, _load_capability_overrides())

    return caps
