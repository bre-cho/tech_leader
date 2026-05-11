from __future__ import annotations

from typing import Any


def apply_emotion(
    subtitles: list[dict[str, Any]],
    voice_tone: str,
    music_beat: float,
) -> list[dict[str, Any]]:
    """Overlay emotion-driven visual effects onto subtitle word objects."""
    for word in subtitles:
        if voice_tone == "excited":
            word["effect"] = "scale+glow"

        if music_beat > 0.7:
            word["effect"] = "pulse"

    return subtitles
