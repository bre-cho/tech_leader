from __future__ import annotations

from typing import Any


def create_render_job_from_script(
    *,
    project_id: str,
    script_output: dict[str, Any],
) -> list[dict[str, Any]]:
    render_scenes = list(script_output.get("render_scenes") or [])
    jobs: list[dict[str, Any]] = []
    for idx, scene in enumerate(render_scenes, start=1):
        jobs.append(
            {
                "project_id": project_id,
                "scene_id": scene.get("scene_id"),
                "scene_index": int(scene.get("scene_index") or idx),
                "render_purpose": scene.get("render_purpose"),
                "voiceover_text": scene.get("voiceover_text") or scene.get("script_text"),
                "duration_sec": float(scene.get("duration_sec") or scene.get("resolved_duration_seconds") or 0.0),
                "drama_metadata": dict(scene.get("drama_metadata") or {}),
            }
        )
    return jobs
