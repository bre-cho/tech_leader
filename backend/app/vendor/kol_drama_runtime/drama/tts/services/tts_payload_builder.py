from __future__ import annotations

from typing import Any


def build_tts_payload(scene_payload: dict[str, Any]) -> dict[str, Any]:
    voice_directive = dict(scene_payload.get("voice_directive") or {})
    drama_metadata = dict(scene_payload.get("drama_metadata") or {})
    text = (
        scene_payload.get("voiceover_text")
        or scene_payload.get("text")
        or ""
    )
    duration_seconds = (
        scene_payload.get("duration_sec")
        or scene_payload.get("duration_seconds")
    )
    return {
        "scene_id": scene_payload.get("scene_id"),
        "text": text,
        "voiceover_text": text,
        "duration_sec": duration_seconds,
        "duration_seconds": duration_seconds,
        "voice_directive": voice_directive,
        "voice_id": scene_payload.get("voice_id") or voice_directive.get("voice_id"),
        "character_id": scene_payload.get("character_id") or scene_payload.get("speaker_id"),
        "emotion": scene_payload.get("emotion") or drama_metadata.get("emotion") or voice_directive.get("tone"),
        "language": scene_payload.get("language") or voice_directive.get("language") or "en",
        "tone": voice_directive.get("tone"),
        "speed": voice_directive.get("speed", "normal"),
        "pause": voice_directive.get("pause", "normal"),
        "stress_words": list(voice_directive.get("stress_words") or []),
        "drama_metadata": drama_metadata,
    }
