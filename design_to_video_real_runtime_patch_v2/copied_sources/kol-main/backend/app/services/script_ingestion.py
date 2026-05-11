from __future__ import annotations

from typing import Any


def estimate_duration(text: str) -> float:
    words = len((text or "").split())
    return max(2.0, round(words / 2.8, 2))


def build_subtitle_segments_from_scenes(scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    cursor = 0.0
    for scene in scenes or []:
        text = str(scene.get("script_text") or "")
        duration = float(scene.get("target_duration_sec") or estimate_duration(text))
        end = cursor + duration
        segments.append(
            {
                "scene_index": scene.get("scene_index"),
                "start_sec": round(cursor, 3),
                "end_sec": round(end, 3),
                "text": text,
            }
        )
        cursor = end
    return segments
