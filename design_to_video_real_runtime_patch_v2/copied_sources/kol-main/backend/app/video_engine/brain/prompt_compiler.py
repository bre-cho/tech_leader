from __future__ import annotations

import json as _json
import logging
import os
import re
import urllib.request
from typing import Any, Dict, List
from .contracts import MultiModalReference, MultiModalVideoIntent, CompiledProviderPayload, BrainMode

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# P9: Optional LLM extraction path
# Set PROMPT_COMPILER_LLM_ENDPOINT=<url> to enable.  The endpoint must accept
# a JSON POST body {"prompt": "<raw>", "task": "segment"} and return:
#   {"subject": "...", "motion": "...", "environment": "...",
#    "aesthetics": "...", "camera": "...", "audio": "..."}
# Falls back to keyword matching when the endpoint is absent or fails.
# ---------------------------------------------------------------------------
_LLM_ENDPOINT = os.environ.get("PROMPT_COMPILER_LLM_ENDPOINT", "").strip()
_LLM_TIMEOUT = int(os.environ.get("PROMPT_COMPILER_LLM_TIMEOUT", "8"))


def _llm_segment(raw_prompt: str) -> Dict[str, str] | None:
    """Call the configured LLM endpoint to extract prompt segments.

    Returns a dict with keys ``subject``, ``motion``, ``environment``,
    ``aesthetics``, ``camera``, ``audio``; or ``None`` when the endpoint is
    unavailable or the response cannot be parsed.

    Only HTTPS endpoints are accepted.  HTTP (plaintext) endpoints are
    rejected to prevent credential leakage and MITM attacks.  Private/
    loopback addresses are blocked to prevent SSRF.
    """
    import ipaddress as _ipaddress  # noqa: PLC0415
    import socket as _socket  # noqa: PLC0415
    from urllib.parse import urlparse as _urlparse  # noqa: PLC0415

    endpoint = os.environ.get("PROMPT_COMPILER_LLM_ENDPOINT", "").strip()
    if not endpoint:
        return None

    # Validate scheme: only HTTPS is accepted to protect credentials in transit.
    parsed = _urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.hostname:
        _logger.warning(
            "PromptCompiler: PROMPT_COMPILER_LLM_ENDPOINT must use https (got %r); "
            "LLM segmentation disabled.",
            parsed.scheme,
        )
        return None

    # Optional hostname allowlist: when PROMPT_COMPILER_LLM_ALLOWED_HOSTS is
    # set (comma-separated), only those hostnames are accepted.  This prevents
    # the endpoint env var from being abused to route requests to arbitrary
    # internal services even when the IP check below passes.
    allowed_hosts_raw = os.environ.get("PROMPT_COMPILER_LLM_ALLOWED_HOSTS", "").strip()
    if allowed_hosts_raw:
        allowed_hosts = {h.strip().lower() for h in allowed_hosts_raw.split(",") if h.strip()}
        if parsed.hostname.lower() not in allowed_hosts:
            _logger.warning(
                "PromptCompiler: PROMPT_COMPILER_LLM_ENDPOINT hostname %r is not in "
                "PROMPT_COMPILER_LLM_ALLOWED_HOSTS (%r); LLM segmentation disabled.",
                parsed.hostname,
                allowed_hosts_raw,
            )
            return None

    # SSRF guard: block requests to private/loopback/reserved addresses.
    hostname = parsed.hostname
    try:
        addr = _ipaddress.ip_address(hostname)
        resolved = [addr]
    except ValueError:
        try:
            infos = _socket.getaddrinfo(hostname, None)
            resolved = [_ipaddress.ip_address(info[4][0]) for info in infos]
        except Exception:  # noqa: BLE001
            resolved = []
    for addr in resolved:
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
            _logger.warning(
                "PromptCompiler: PROMPT_COMPILER_LLM_ENDPOINT resolves to a private/loopback "
                "address (%s); LLM segmentation disabled to prevent SSRF.",
                addr,
            )
            return None

    try:
        payload = _json.dumps({"prompt": raw_prompt, "task": "segment"}).encode()
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=_LLM_TIMEOUT) as resp:  # noqa: S310
            result: dict[str, Any] = _json.loads(resp.read())
        required = {"subject", "motion", "environment", "aesthetics", "camera"}
        if required.issubset(result.keys()):
            return {k: str(result.get(k) or "") for k in ("subject", "motion", "environment", "aesthetics", "camera", "audio")}
        return None
    except Exception as exc:  # noqa: BLE001
        _logger.debug("PromptCompiler LLM segment failed (%s); falling back to keyword matching", exc)
        return None


def _segment(raw: str, keywords: List[str], fallback: str = "") -> str:
    lower = raw.lower()
    hits = [kw for kw in keywords if kw in lower]
    if hits:
        return raw
    return fallback


class PromptCompiler:
    """Converts raw user render request into intent and provider payload.

    This is deterministic and safe.  Prompt segmentation uses an optional LLM
    extraction path (``PROMPT_COMPILER_LLM_ENDPOINT``) that works for any
    language including Vietnamese.  When the LLM endpoint is absent or fails,
    the deterministic keyword-matching fallback is used so the compiler is
    always usable offline.
    """

    def build_intent(
        self,
        request: Dict[str, Any],
        project_context: Dict[str, Any] | None = None,
    ) -> MultiModalVideoIntent:
        """Build a :class:`MultiModalVideoIntent` from a raw render request.

        When *project_context* is supplied (typically ``ProjectProfile.to_context()``)
        the intent is enriched with the project's visual aesthetics, aspect ratio,
        quality tier, and negative-prompt defaults so every render stays anchored to
        the project identity.

        Segmentation order:
        1. LLM extraction via ``PROMPT_COMPILER_LLM_ENDPOINT`` (language-agnostic).
        2. Keyword matching fallback (Latin keywords only).
        """
        ctx = project_context or {}
        prompt = request.get("prompt") or ""
        refs: List[MultiModalReference] = []
        if request.get("reference_image_url"):
            refs.append(MultiModalReference(kind="image", url=str(request["reference_image_url"]), role="subject", weight=1.0))
        if request.get("reference_video_url"):
            refs.append(MultiModalReference(kind="video", url=str(request["reference_video_url"]), role="motion", weight=0.9))
        audio = request.get("audio") or {}
        if audio.get("reference_audio_url"):
            refs.append(MultiModalReference(kind="audio", url=str(audio["reference_audio_url"]), role="audio", weight=0.8))

        mode = request.get("mode", "text_to_video")
        if refs and mode == "text_to_video":
            mode = "reference_to_video"

        # Project-context defaults (override only when request omits the field)
        aspect_ratio = request.get("aspect_ratio") or ctx.get("aspect_ratio", "16:9")
        quality_tier = request.get("quality_tier") or ctx.get("quality_tier", "standard")
        negative_prompt = (
            request.get("negative_prompt")
            or ctx.get("negative_prompt_defaults")
            or "low quality, warped anatomy, flicker, unreadable text, watermark"
        )

        # Enrich aesthetics segment with project visual style
        visual_style = ctx.get("visual_style", "")

        # --- P9: Try LLM segmentation first; fall back to keyword matching ---
        llm_segments = _llm_segment(prompt) if prompt else None

        if llm_segments:
            subject = llm_segments.get("subject") or prompt[:300]
            motion = llm_segments.get("motion") or "natural cinematic motion"
            environment = llm_segments.get("environment") or "environment derived from prompt"
            aesthetics_base = llm_segments.get("aesthetics") or "cinematic realistic high detail"
            camera = llm_segments.get("camera") or "stable cinematic camera, full subject visible"
            audio_seg = llm_segments.get("audio") or ""
        else:
            subject = _segment(prompt, ["person", "model", "avatar", "product", "car", "character"], prompt[:300])
            motion = _segment(prompt, ["walk", "run", "camera", "pan", "dolly", "zoom", "rotate", "move"], "natural cinematic motion")
            environment = _segment(prompt, ["studio", "street", "room", "city", "forest", "background"], "environment derived from prompt")
            aesthetics_base = _segment(
                prompt,
                ["cinematic", "realistic", "luxury", "documentary", "anime", "editorial"],
                "cinematic realistic high detail",
            )
            camera = _segment(prompt, ["close-up", "wide", "low angle", "top shot", "dolly", "handheld", "tracking"], "stable cinematic camera, full subject visible")
            audio_seg = ""

        aesthetics = f"{aesthetics_base}, {visual_style}".strip(", ") if visual_style else aesthetics_base
        audio_field = audio.get("prompt") or audio_seg or ("native synchronized audio" if audio.get("enabled") else "")

        return MultiModalVideoIntent(
            raw_prompt=prompt,
            subject=subject,
            motion=motion,
            environment=environment,
            aesthetics=aesthetics,
            camera=camera,
            audio=audio_field,
            negative_prompt=negative_prompt,
            mode=BrainMode(mode),
            aspect_ratio=aspect_ratio,
            duration_seconds=int(request.get("duration_seconds", ctx.get("default_scene_duration_seconds", 8))),
            quality_tier=quality_tier,
            seed=request.get("seed"),
            references=refs,
            metadata={**(request.get("metadata") or {}), "project_context": ctx} if ctx else (request.get("metadata") or {}),
        )

    def compile_for_provider(
        self,
        intent: MultiModalVideoIntent,
        provider: str,
        model: str | None = None,
        project_context: Dict[str, Any] | None = None,
    ) -> CompiledProviderPayload:
        prompt = self._compose_prompt(intent, provider, project_context=project_context)
        options: Dict[str, Any] = {}
        if provider == "seedance":
            options.update({"reference_mapping": [r.model_dump() for r in intent.references], "enable_text_overlay_guard": True})
        elif provider == "veo":
            options.update({"cinematic_strength": "high", "audio_generation": bool(intent.audio)})
        elif provider == "runway":
            options.update({"motion_strength": 0.55, "style_preservation": 0.7})
        elif provider == "kling":
            options.update({"cfg_scale": 0.5})

        return CompiledProviderPayload(
            provider=provider,
            model=model,
            mode=intent.mode.value,
            prompt=prompt,
            negative_prompt=intent.negative_prompt,
            aspect_ratio=intent.aspect_ratio,
            duration_seconds=intent.duration_seconds,
            seed=intent.seed,
            references=[r.model_dump() for r in intent.references],
            audio={"enabled": bool(intent.audio), "prompt": intent.audio},
            provider_options=options,
        )

    def _compose_prompt(
        self,
        intent: MultiModalVideoIntent,
        provider: str,
        project_context: Dict[str, Any] | None = None,
    ) -> str:
        ctx = project_context or {}
        blocks = [
            f"Subject: {intent.subject}",
            f"Motion: {intent.motion}",
            f"Environment: {intent.environment}",
            f"Aesthetics: {intent.aesthetics}",
            f"Camera: {intent.camera}",
        ]
        if intent.audio:
            blocks.append(f"Audio: {intent.audio}")
        if intent.references:
            ref_text = "; ".join([f"{r.kind}:{r.role}:weight={r.weight}" for r in intent.references])
            blocks.append(f"Reference mapping: {ref_text}")
        # Franchise identity layer — inject project brand voice when available
        if ctx.get("visual_style"):
            blocks.append(f"Brand visual style: {ctx['visual_style']}")
        if ctx.get("colour_palette"):
            blocks.append(f"Colour palette: {', '.join(ctx['colour_palette'][:3])}")
        if ctx.get("archetype"):
            blocks.append(f"Character archetype: {ctx['archetype']}")
        blocks.append("Composition rule: keep full subject in frame, no crop, coherent temporal motion.")
        return "\n".join(blocks)



class VideoPromptCompiler(PromptCompiler):
    """Visual Engine V4 compatibility compiler.

    .. deprecated:: 2026.05
        This class is deprecated and will be removed in Q3/2026.
        Use :class:`PromptCompiler` directly — call
        :meth:`PromptCompiler.build_intent` and
        :meth:`PromptCompiler.compile_for_provider` instead.
        The ``compile()`` method below is provided for reference only.

    Extends :class:`PromptCompiler` with the V4 ``compile()`` interface.
    """

    def compile(
        self,
        prompt: str,
        character_dna: dict,
        style_lock: dict,
        motion_template: dict,
        constraints: dict,
    ) -> dict:
        """Compile a V4-style prompt payload from raw parameters.

        .. deprecated:: 2026.05
            Use :meth:`PromptCompiler.build_intent` and
            :meth:`PromptCompiler.compile_for_provider` instead.
            This method will be removed in Q3/2026.
        """
        import warnings  # noqa: PLC0415
        warnings.warn(
            "VideoPromptCompiler.compile() is deprecated since 2026.05 and will be "
            "removed in Q3/2026. Use PromptCompiler.build_intent() + "
            "PromptCompiler.compile_for_provider() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return {
            "video_prompt": (
                f"{prompt}. Same consistent character DNA: {character_dna}. "
                f"Style lock: {style_lock}. Motion template: {motion_template}. "
                "High converting ad creative, clear CTA, high contrast, no clutter."
            ),
            "negative_prompt": (
                "random face, inconsistent outfit, flat lighting, cluttered layout, "
                "too much text, unreadable Vietnamese, watermark, logo"
            ),
            "aspect_ratio": constraints.get("aspect_ratio", "9:16"),
            "duration_seconds": constraints.get("duration_seconds", 5),
        }
