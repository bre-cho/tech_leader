from __future__ import annotations

from app.shared.artifacts import make_artifact
from app.shared.ffmpeg import mix_timeline_ffmpeg
from app.voice.contracts import TimelineMixRequest, TimelineMixResponse


class RealVoiceTimelineMixService:
    def mix(self, req: TimelineMixRequest) -> TimelineMixResponse:
        out = mix_timeline_ffmpeg(req.clips, req.output_path, req.target_lufs)
        artifact = make_artifact(
            path=out,
            artifact_type="voice_timeline_audio_mix",
            source_job_id=req.job_id,
            created_by="ffmpeg_voice_timeline_mix",
            mime_type="audio/aac",
            metadata={"clips": req.clips, "target_lufs": req.target_lufs},
        )
        return TimelineMixResponse(status="succeeded", output_path=out, artifact=artifact.model_dump())
