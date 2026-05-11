"""drama_veo_prompt_translator — converts Drama Engine instructions to Veo visual prompts.

The Veo API only accepts a free-text ``prompt`` field; it has no structured
parameters for acting tempo, gaze, camera mode, or blocking.  This module
translates the rich Drama Engine / RenderBridgeService payload into natural
language extensions that are appended to the base scene ``visual_prompt``
before the scene is submitted to Veo.

Usage
-----
::

    from app.services.drama.drama_veo_prompt_translator import DramaVeoPromptTranslator

    translator = DramaVeoPromptTranslator()
    enhanced_prompt = translator.translate(
        base_prompt="Two characters argue in a dimly lit room.",
        bridge_payload=render_bridge_service.build(...),
    )
    # enhanced_prompt is ready to pass as the Veo ``prompt`` field.
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Lookup tables — natural language phrases for each drama value
# ---------------------------------------------------------------------------

_CAMERA_MODE_PHRASES: dict[str, str] = {
    "power_instability": "unstable handheld camera emphasising shifting power dynamics",
    "high_tension_lockdown": "tight locked-off framing with minimal movement, extreme tension",
    "rising_conflict": "slow deliberate push-in as conflict escalates",
    "neutral_observe": "observational medium shot, camera holds steady",
}

_CAMERA_MOVEMENT_PHRASES: dict[str, str] = {
    "controlled_push_in_at_exposure": "controlled push-in at the moment of exposure",
    "slow_push_reveal": "slow push-in revealing hidden truth",
    "arc_in_at_reveal": "arc movement inward at the moment of revelation",
    "push_in_steady": "steady push-in during confrontation",
    "slow_dolly_in": "slow dolly-in as character confesses",
    "static_observational": "static observational framing",
}

_TEMPO_PHRASES: dict[str, str] = {
    "fast": "rapid speech delivery",
    "quick": "quick energetic delivery",
    "moderate": "measured conversational pacing",
    "slow": "deliberate slow speech delivery",
    "very_slow": "extremely slow and weighted delivery",
}

_GAZE_PHRASES: dict[str, str] = {
    "direct": "direct eye contact with the other character",
    "avoidant": "avoiding eye contact, gaze cast slightly downward",
    "challenging": "challenging defiant stare",
    "distant": "distant unfocused gaze",
    "neutral": "neutral gaze",
}

_MICRO_EXPRESSION_PHRASES: dict[str, str] = {
    "guilt": "subtle guilt visible in micro-expressions",
    "defiance": "micro-expressions of defiance and resistance",
    "fear": "barely suppressed fear in facial micro-expressions",
    "contempt": "flash of contempt crossing the face",
    "grief": "grief visible through subtle facial tremors",
    "neutral": "",
}

_VOICE_PRESSURE_PHRASES: dict[str, str] = {
    "sharp_rising": "sharp rising vocal pressure",
    "high_sharp": "high sharp vocal intensity",
    "low_controlled": "low controlled deliberate tone",
    "whispered": "near whisper, intimate and intense",
    "normal": "",
}

_MOVEMENT_PHRASES: dict[str, str] = {
    "aggressive_forward": "aggressive forward body movement",
    "retreat_backed": "backing away retreating body language",
    "frozen_rigid": "frozen rigid body stance",
    "neutral_balanced": "",
}

_TEMPERATURE_PHRASES: dict[str, str] = {
    "explosive": "explosive emotional atmosphere",
    "heated": "heated charged atmosphere",
    "cold": "cold tense atmosphere",
    "warm": "warm intimate atmosphere",
}

# Outcome types that warrant an explicit cinematic label in the Veo prompt.
_CINEMATIC_OUTCOME_TYPES: frozenset[str] = frozenset({"betrayal", "exposure", "moral_power_flip"})


# ---------------------------------------------------------------------------
# Main translator
# ---------------------------------------------------------------------------

class DramaVeoPromptTranslator:
    """Converts a RenderBridgeService payload to natural-language Veo prompt extensions.

    Only non-trivial acting/camera values are appended; neutral/empty values
    are silently omitted so the base prompt is not polluted with filler words.
    """

    def translate(
        self,
        base_prompt: str,
        bridge_payload: dict[str, Any],
    ) -> str:
        """Return a Veo-ready prompt string enriched with drama instructions.

        Parameters
        ----------
        base_prompt:
            The original scene visual prompt (plain English / Vietnamese).
        bridge_payload:
            Output dict from :class:`~app.services.drama.render_bridge_service.RenderBridgeService.build`.

        Returns
        -------
        str
            The base prompt with drama/acting/camera language appended.
        """
        parts: list[str] = [base_prompt.strip()]

        drama_state: dict[str, Any] = bridge_payload.get("drama_state") or {}
        camera_plan: dict[str, Any] = bridge_payload.get("camera_plan") or {}
        character_updates: list[dict[str, Any]] = bridge_payload.get("character_updates") or []

        # Scene atmosphere
        temperature = str(drama_state.get("scene_temperature") or "")
        if temperature in _TEMPERATURE_PHRASES and _TEMPERATURE_PHRASES[temperature]:
            parts.append(_TEMPERATURE_PHRASES[temperature])

        # Camera
        cam_mode = str(camera_plan.get("mode") or "")
        cam_phrase = _CAMERA_MODE_PHRASES.get(cam_mode, "")
        if cam_phrase:
            parts.append(cam_phrase)

        cam_movement = str(camera_plan.get("movement") or "")
        mov_phrase = _CAMERA_MOVEMENT_PHRASES.get(cam_movement, "")
        if mov_phrase:
            parts.append(mov_phrase)

        # Acting instructions for each character
        for update in character_updates:
            acting: dict[str, str] = update.get("acting") or {}
            acting_parts: list[str] = []

            tempo_phrase = _TEMPO_PHRASES.get(str(acting.get("tempo") or ""), "")
            if tempo_phrase:
                acting_parts.append(tempo_phrase)

            gaze_phrase = _GAZE_PHRASES.get(str(acting.get("gaze") or ""), "")
            if gaze_phrase:
                acting_parts.append(gaze_phrase)

            expr_phrase = _MICRO_EXPRESSION_PHRASES.get(str(acting.get("micro_expression") or ""), "")
            if expr_phrase:
                acting_parts.append(expr_phrase)

            pressure_phrase = _VOICE_PRESSURE_PHRASES.get(str(acting.get("voice_pressure") or ""), "")
            if pressure_phrase:
                acting_parts.append(pressure_phrase)

            movement_phrase = _MOVEMENT_PHRASES.get(str(acting.get("movement") or ""), "")
            if movement_phrase:
                acting_parts.append(movement_phrase)

            if acting_parts:
                parts.append(", ".join(acting_parts))

        # Outcome hint for cinematic context
        outcome = str(drama_state.get("outcome_type") or "")
        if outcome in _CINEMATIC_OUTCOME_TYPES:
            parts.append(f"cinematic {outcome.replace('_', ' ')} scene")

        return ". ".join(filter(None, parts))

    def translate_scene_payload(self, scene_payload: dict[str, Any]) -> dict[str, Any]:
        """Enrich a scene submission payload in-place if bridge data is present.

        If ``scene_payload`` contains a ``drama_bridge`` key (set by
        ``RenderBridgeService``), the ``prompt`` / ``visual_prompt`` field is
        extended with the translated drama instructions.  The original payload
        is returned (mutated) for convenience.

        Parameters
        ----------
        scene_payload:
            The dict passed to ``VeoAdapter.submit()``.  Must contain at least
            a ``prompt`` or ``visual_prompt`` key.

        Returns
        -------
        dict[str, Any]
            The same ``scene_payload`` dict, possibly with an enriched prompt.
        """
        bridge = scene_payload.get("drama_bridge")
        if not bridge:
            return scene_payload

        base = (
            scene_payload.get("prompt")
            or scene_payload.get("visual_prompt")
            or scene_payload.get("description")
            or ""
        )
        enhanced = self.translate(base_prompt=base, bridge_payload=bridge)

        # Write back to whichever key was present
        if "prompt" in scene_payload:
            scene_payload["prompt"] = enhanced
        elif "visual_prompt" in scene_payload:
            scene_payload["visual_prompt"] = enhanced
        else:
            scene_payload["prompt"] = enhanced

        return scene_payload
