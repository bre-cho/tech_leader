from __future__ import annotations

from typing import Any

from app.drama.timeline.engines.subtitle_timing_engine import compile_subtitle_timing
from app.drama.timeline.schemas.timeline_request import TimelineRequest


class _TimelineCompiler:
    def compile(
        self,
        *,
        project_id: str,
        episode_id: str,
        render_scenes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        scenes: list[dict[str, Any]] = []
        cursor = 0.0
        for idx, scene in enumerate(render_scenes or [], start=1):
            duration = float(scene.get("duration_sec") or scene.get("resolved_duration_seconds") or 0.0)
            start_sec = round(cursor, 3)
            end_sec = round(cursor + max(0.0, duration), 3)
            scenes.append(
                {
                    "scene_index": int(scene.get("scene_index") or idx),
                    "scene_id": scene.get("scene_id"),
                    "title": scene.get("title"),
                    "start_sec": start_sec,
                    "end_sec": end_sec,
                    "duration_sec": round(max(0.0, duration), 3),
                    "video_url": scene.get("video_url"),
                }
            )
            cursor = end_sec
        return {
            "project_id": project_id,
            "episode_id": episode_id,
            "total_duration_sec": round(cursor, 3),
            "scene_timeline": scenes,
            "subtitle_segments": compile_subtitle_timing(render_scenes or []),
        }


class TimelineService:
    def __init__(self) -> None:
        self.compiler = _TimelineCompiler()

    def compile(self, payload: TimelineRequest) -> dict[str, Any]:
        return self.compiler.compile(
            project_id=payload.project_id,
            episode_id=payload.episode_id,
            render_scenes=payload.render_scenes,
        )
