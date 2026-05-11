from __future__ import annotations

import threading
from typing import Any, Dict, List, Tuple

from .capability_registry import default_capabilities
from .contracts import MultiModalVideoIntent, ProviderCapability


ROUTING_PROFILES = {
    # "fal" has been removed from all profiles: no FalAdapter exists in providers/
    # and routing to an unregistered provider raises ValueError in production.
    # Re-add "fal" here only after a FalAdapter is implemented and prod-guarded.
    "cinematic_ads": ["seedance", "veo", "runway", "kling", "local_stub"],
    "character_consistency": ["seedance", "runway", "kling", "veo", "local_stub"],
    "realism_audio_native": ["veo", "seedance", "runway", "local_stub"],
    "fast_social_test": ["seedance", "runway", "kling", "local_stub"],
    # social_fast: optimised for short-form 9:16 social ads where generation
    # speed matters more than cinematic quality.  Seedance2 leads (fastest,
    # lowest cost), falling back to seedance then kling.
    "social_fast": ["seedance2", "seedance", "kling", "local_stub"],
    "editing": ["seedance", "runway", "local_stub"],
    "lowest_cost": ["kling", "seedance2", "seedance", "runway", "local_stub"],
}


# ---------------------------------------------------------------------------
# ROUTING_PROFILES validation
# ---------------------------------------------------------------------------

# Guards against typos / removed providers silently turning into rejected
# candidates.  "local_stub" is excluded from the check because it is
# intentionally absent from production capabilities (guarded by
# capability_registry.default_capabilities()) and its absence is handled
# gracefully by CapabilityRouter.evaluate().

_PROFILES_VALIDATED = False
# Lock protecting the module-level _PROFILES_VALIDATED flag so concurrent
# CapabilityRouter construction in multi-threaded servers validates exactly
# once rather than zero or many times.
_PROFILES_VALIDATED_LOCK = threading.Lock()


def _validate_routing_profiles(caps: Dict[str, ProviderCapability]) -> None:
    """Assert every non-stub provider in ROUTING_PROFILES exists in *caps*.

    Raises :class:`ValueError` on the first missing provider so startup fails
    fast rather than silently routing all requests through a shorter list.
    """
    for profile, providers in ROUTING_PROFILES.items():
        for provider in providers:
            if provider == "local_stub":
                # local_stub is intentionally excluded from production caps;
                # absent entries are gracefully rejected during routing.
                continue
            if provider not in caps:
                raise ValueError(
                    f"ROUTING_PROFILES[{profile!r}] references unregistered provider "
                    f"{provider!r}. Register a ProviderCapability in "
                    "capability_registry.default_capabilities() or remove the provider "
                    "from the profile."
                )


class CapabilityRouter:
    def __init__(self, capabilities: Dict[str, ProviderCapability] | None = None):
        global _PROFILES_VALIDATED
        self.capabilities = capabilities or default_capabilities()
        if capabilities is None:
            # Production path: validate routing profiles exactly once per process.
            # Use a double-checked lock so concurrent first-time constructions in
            # a multi-threaded server don't race: the outer check is a fast path
            # that avoids acquiring the lock on every request once validated; the
            # inner check prevents a second validation if two threads both saw
            # _PROFILES_VALIDATED=False before either acquired the lock.
            if not _PROFILES_VALIDATED:
                with _PROFILES_VALIDATED_LOCK:
                    if not _PROFILES_VALIDATED:
                        _validate_routing_profiles(self.capabilities)
                        _PROFILES_VALIDATED = True
        # Custom capabilities (e.g. in tests or routing experiments): skip the
        # global flag entirely.  Each custom-caps instance is self-contained;
        # it cannot interfere with the production validation flag and does not
        # require all production providers to be present.

    def candidate_chain(self, routing_profile: str, requested_provider: str = "auto") -> List[str]:
        if requested_provider and requested_provider != "auto":
            return [requested_provider]
        return ROUTING_PROFILES.get(routing_profile, ROUTING_PROFILES["cinematic_ads"])

    def evaluate(self, intent: MultiModalVideoIntent, chain: List[str]) -> Tuple[List[ProviderCapability], List[Dict[str, Any]]]:
        eligible: List[ProviderCapability] = []
        rejected: List[Dict[str, Any]] = []
        needs_image = any(r.kind == "image" for r in intent.references)
        needs_video = any(r.kind == "video" for r in intent.references)
        needs_audio_ref = any(r.kind == "audio" for r in intent.references)
        for name in chain:
            cap = self.capabilities.get(name)
            if not cap:
                rejected.append({"provider": name, "reason": "not registered in capability registry"})
                continue
            reason = self._reject_reason(cap, intent, needs_image, needs_video, needs_audio_ref)
            if reason:
                rejected.append({"provider": name, "reason": reason})
            else:
                eligible.append(cap)
        return eligible, rejected

    def _reject_reason(self, cap: ProviderCapability, intent: MultiModalVideoIntent, needs_image: bool, needs_video: bool, needs_audio_ref: bool) -> str | None:
        if intent.mode.value not in cap.modes:
            return f"mode not supported: {intent.mode.value}"
        if intent.aspect_ratio not in cap.aspect_ratios:
            return f"aspect ratio not supported: {intent.aspect_ratio}"
        if intent.duration_seconds > cap.max_duration_seconds:
            return f"duration {intent.duration_seconds}s exceeds max {cap.max_duration_seconds}s"
        if intent.audio and not cap.supports_audio:
            return "audio required but unsupported"
        if needs_image and not cap.supports_image_reference:
            return "image reference required but unsupported"
        if needs_video and not cap.supports_video_reference:
            return "video reference required but unsupported"
        if needs_audio_ref and not cap.supports_audio_reference:
            return "audio reference required but unsupported"
        if intent.mode.value == "video_edit" and not cap.supports_video_editing:
            return "video editing required but unsupported"
        if intent.mode.value == "video_extend" and not cap.supports_video_extension:
            return "video extension required but unsupported"
        return None
