from __future__ import annotations

from typing import Any


def build_final_preview_timeline(
    *,
    scenes: list[dict[str, Any]],
    subtitle_segments: list[dict[str, Any]] | None = None,
    merged_video_url: str | None = None,
) -> dict[str, Any]:
    normalized_scenes: list[dict[str, Any]] = []
    for scene in scenes or []:
        normalized_scenes.append(
            {
                "scene_index": scene.get("scene_index"),
                "title": scene.get("title"),
                "video_url": scene.get("video_url") or scene.get("output_video_url"),
                "local_video_path": scene.get("local_video_path"),
            }
        )
    return {
        "merged_video_url": merged_video_url,
        "scenes": normalized_scenes,
        "subtitle_segments": list(subtitle_segments or []),
    }
