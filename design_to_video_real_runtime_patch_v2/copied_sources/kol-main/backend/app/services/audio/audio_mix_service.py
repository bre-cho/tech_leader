from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.production_gate import is_production_env
from app.models.audio_mix_profile import AudioMixProfile
from app.models.audio_render_output import AudioRenderOutput
from app.models.music_asset import MusicAsset
from app.models.narration_job import NarrationJob
from app.services.object_storage import upload_file_to_object_storage

_logger = logging.getLogger(__name__)


def _loudnorm_enabled() -> bool:
    """Return True when post-mix loudness normalisation is enabled.

    Defaults to ``True`` in production/staging (broadcast-grade output) and
    ``False`` in local development to avoid the extra FFmpeg pass during testing.
    Override either way with the ``AUDIO_LOUDNORM_ENABLED`` environment variable.
    """
    val = os.getenv("AUDIO_LOUDNORM_ENABLED")
    if val is not None:
        return val.strip().lower() in {"1", "true", "yes", "on"}
    return is_production_env()


def ensure_default_mix_profile(db: Session) -> AudioMixProfile:
    row = db.query(AudioMixProfile).order_by(AudioMixProfile.created_at.asc()).first()
    if row:
        return row
    row = AudioMixProfile(display_name="Default cinematic mix")
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_audio_render_output(
    db: Session,
    *,
    render_job_id: str | None,
    narration_job_id: str,
    music_asset_id: str | None,
    mix_profile_id: str | None,
) -> AudioRenderOutput:
    profile = db.query(AudioMixProfile).filter(AudioMixProfile.id == mix_profile_id).first() if mix_profile_id else ensure_default_mix_profile(db)
    output = AudioRenderOutput(
        render_job_id=render_job_id,
        narration_job_id=narration_job_id,
        music_asset_id=music_asset_id,
        mix_profile_id=profile.id if profile else None,
        status="queued",
    )
    db.add(output)
    db.commit()
    db.refresh(output)
    return output


def mix_audio_tracks(db: Session, audio_output_id: str) -> AudioRenderOutput:
    output = db.query(AudioRenderOutput).filter(AudioRenderOutput.id == audio_output_id).first()
    if output is None:
        raise ValueError(f"Audio output not found: {audio_output_id}")

    narration = db.query(NarrationJob).filter(NarrationJob.id == output.narration_job_id).first()
    music = db.query(MusicAsset).filter(MusicAsset.id == output.music_asset_id).first() if output.music_asset_id else None

    if narration is None or not narration.output_local_path:
        output.status = "failed"
        output.error_message = "Narration audio is missing"
        db.commit()
        return output

    voice_path = Path(narration.output_local_path)
    output.voice_track_url = narration.output_url
    output.status = "processing"
    db.commit()

    target_dir = Path(settings.audio_output_dir) / "mix" / output.id
    target_dir.mkdir(parents=True, exist_ok=True)
    mixed_path = target_dir / "mixed_audio.mp3"

    if music and music.local_path:
        output.music_track_url = music.public_url
        cmd = [
            settings.ffmpeg_binary,
            "-y",
            "-i", str(voice_path),
            "-i", str(music.local_path),
            "-filter_complex",
            "amix=inputs=2:duration=longest:dropout_transition=2",
            "-c:a", "mp3",
            str(mixed_path),
        ]
    else:
        cmd = [
            settings.ffmpeg_binary,
            "-y",
            "-i", str(voice_path),
            "-c:a", "copy",
            str(mixed_path),
        ]

    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=int(os.getenv("FFMPEG_AUDIO_MIX_TIMEOUT_SEC", "300")),
    )
    if completed.returncode != 0:
        output.status = "failed"
        output.error_message = completed.stderr[-4000:]
        try:
            log_path = target_dir / "ffmpeg_error.log"
            log_path.write_text(
                f"cmd: {' '.join(cmd)}\n"
                f"returncode: {completed.returncode}\n"
                f"--- stdout ---\n{completed.stdout}\n"
                f"--- stderr ---\n{completed.stderr}\n"
            )
            output.error_artifact_url = f"/artifacts/audio/mix/{output.id}/ffmpeg_error.log"
        except OSError:
            pass
        db.commit()
        return output

    output.local_mixed_audio_path = str(mixed_path)

    # Optional loudness normalization pass (EBU R128 target: -16 LUFS).
    # Enabled by default in production to produce broadcast-grade audio.
    # Disable via AUDIO_LOUDNORM_ENABLED=false or set AUDIO_LOUDNORM_ENABLED=true to force.
    if _loudnorm_enabled():
        normalized_path = target_dir / "mixed_audio_normalized.mp3"
        norm_cmd = [
            settings.ffmpeg_binary,
            "-y",
            "-i", str(mixed_path),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(normalized_path),
        ]
        try:
            norm_result = subprocess.run(
                norm_cmd,
                capture_output=True,
                text=True,
                timeout=int(os.getenv("FFMPEG_AUDIO_MIX_TIMEOUT_SEC", "300")),
            )
            if norm_result.returncode == 0:
                mixed_path = normalized_path
                output.local_mixed_audio_path = str(mixed_path)
            else:
                _logger.warning(
                    "audio loudnorm pass failed for output=%s (non-fatal, using unnormalized mix): %s",
                    output.id,
                    norm_result.stderr[-1000:],
                )
        except subprocess.TimeoutExpired:
            _logger.warning(
                "audio loudnorm pass timed out after %ss for output=%s (non-fatal)",
                int(os.getenv("FFMPEG_AUDIO_MIX_TIMEOUT_SEC", "300")),
                output.id,
            )

    key = f"audio/mix/{output.id}/mixed_audio.mp3"
    try:
        stored = upload_file_to_object_storage(local_path=str(mixed_path), key=key, content_type="audio/mpeg")
        output.mixed_audio_url = stored.public_url
    except Exception:
        output.mixed_audio_url = f"/artifacts/audio/mix/{output.id}/mixed_audio.mp3"

    output.status = "succeeded"
    db.commit()
    db.refresh(output)
    return output
