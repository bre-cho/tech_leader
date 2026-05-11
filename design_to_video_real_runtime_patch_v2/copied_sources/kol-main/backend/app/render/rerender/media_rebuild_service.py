from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.render_job import RenderJob
from app.models.render_scene_task import RenderSceneTask
from app.services.artifact_lineage_service import record_file_artifact


def _srt_ts(seconds: float) -> str:
    seconds = max(0.0, float(seconds or 0.0)); ms = int(round((seconds - int(seconds)) * 1000)); whole = int(seconds)
    return f"{whole//3600:02d}:{(whole%3600)//60:02d}:{whole%60:02d},{ms:03d}"


def _ass_ts(seconds: float) -> str:
    seconds = max(0.0, float(seconds or 0.0)); cs = int(round((seconds - int(seconds)) * 100)); whole = int(seconds)
    return f"{whole//3600}:{(whole%3600)//60:02d}:{whole%60:02d}.{cs:02d}"


def _extract_payload(scene: RenderSceneTask) -> dict[str, Any]:
    try:
        raw = json.loads(scene.request_payload_json or "{}")
        return raw if isinstance(raw, dict) else {}
    except json.JSONDecodeError:
        return {}


class RerenderMediaRebuildService:
    """Rebuild audio/subtitle/timeline metadata around rerendered scenes."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage_root = Path(settings.storage_root or "storage")

    def rebuild_for_scene(self, *, job: RenderJob, scene: RenderSceneTask, change_type: str, override_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = _extract_payload(scene)
        if override_payload:
            payload.update(override_payload)
        duration = float(payload.get("duration") or payload.get("duration_sec") or 5.0)
        subtitle_text = str(payload.get("subtitle_text") or payload.get("voiceover") or payload.get("title") or scene.title or f"Scene {scene.scene_index + 1}")
        voiceover = str(payload.get("voiceover") or subtitle_text)

        base = self.storage_root / "renders" / str(job.project_id) / str(job.id) / "rerender_media" / f"scene_{scene.scene_index:04d}"
        base.mkdir(parents=True, exist_ok=True)
        srt_path, ass_path = base / "subtitles.srt", base / "subtitles.ass"
        timeline_path, audio_manifest_path = base / "timeline_patch.json", base / "audio_rebuild_manifest.json"

        srt_path.write_text(f"1\n{_srt_ts(0)} --> {_srt_ts(duration)}\n{subtitle_text.strip()}\n", encoding="utf-8")
        ass_path.write_text(
            "[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n"
            "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
            "Style: Default,Arial,54,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,1,2,80,80,96,1\n\n"
            "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
            f"Dialogue: 0,{_ass_ts(0)},{_ass_ts(duration)},Default,,0,0,0,,{subtitle_text}\n",
            encoding="utf-8",
        )
        audio_manifest = {"status": "dirty_requires_audio_render" if change_type in {"audio", "both", "script", "voice"} else "audio_unchanged", "voiceover": voiceover, "duration_sec": duration, "scene_index": scene.scene_index, "render_job_id": job.id}
        audio_manifest_path.write_text(json.dumps(audio_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        timeline_patch = {"scene_index": scene.scene_index, "duration_sec": duration, "subtitle_srt_path": str(srt_path), "subtitle_ass_path": str(ass_path), "audio_manifest_path": str(audio_manifest_path), "requires_audio_render": audio_manifest["status"] == "dirty_requires_audio_render"}
        timeline_path.write_text(json.dumps(timeline_patch, ensure_ascii=False, indent=2), encoding="utf-8")

        for kind, path, meta in [("subtitle_srt", srt_path, timeline_patch), ("subtitle_ass", ass_path, timeline_patch), ("audio_manifest", audio_manifest_path, audio_manifest), ("timeline_patch", timeline_path, timeline_patch)]:
            record_file_artifact(self.db, artifact_type=kind, path=str(path), project_id=job.project_id, render_job_id=job.id, scene_task_id=scene.id, metadata=meta, commit=False)

        payload.update({"duration": duration, "duration_sec": duration, "subtitle_text": subtitle_text, "voiceover": voiceover, "subtitle_srt_path": str(srt_path), "subtitle_ass_path": str(ass_path), "audio_rebuild_manifest_path": str(audio_manifest_path), "timeline_patch_path": str(timeline_path), "media_rebuild_required": True, "audio_rebuild_required": audio_manifest["status"] == "dirty_requires_audio_render"})
        scene.request_payload_json = json.dumps(payload, ensure_ascii=False, default=str)
        return {**timeline_patch, "audio_rebuild_required": payload["audio_rebuild_required"]}
