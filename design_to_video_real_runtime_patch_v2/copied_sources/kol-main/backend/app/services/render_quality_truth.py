from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.render_artifact_service import RenderArtifactError


@dataclass(frozen=True)
class MediaProbeReport:
    ok: bool
    path: str
    size_bytes: int
    duration_seconds: float | None
    width: int | None
    height: int | None
    video_codec: str | None
    audio_codec: str | None
    has_video: bool
    has_audio: bool
    errors: list[str]
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "duration_seconds": self.duration_seconds,
            "width": self.width,
            "height": self.height,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "has_video": self.has_video,
            "has_audio": self.has_audio,
            "errors": self.errors,
            "raw": self.raw,
        }


def ffprobe_media(path: str) -> MediaProbeReport:
    p = Path(path)
    errors: list[str] = []
    if not p.exists():
        return MediaProbeReport(False, path, 0, None, None, None, None, None, False, False, ["file_missing"], {})
    size = p.stat().st_size
    if size <= 0:
        errors.append("zero_byte_file")

    ffprobe = getattr(settings, "ffprobe_binary", "ffprobe") or "ffprobe"
    cmd = [ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(p)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    if result.returncode != 0:
        errors.append(f"ffprobe_failed:{result.stderr[-1000:]}")
        return MediaProbeReport(False, path, size, None, None, None, None, None, False, False, errors, {})

    raw = json.loads(result.stdout or "{}")
    streams = raw.get("streams") or []
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    duration = None
    try:
        duration = float((raw.get("format") or {}).get("duration"))
    except Exception:
        duration = None

    width = int(video.get("width")) if video and video.get("width") else None
    height = int(video.get("height")) if video and video.get("height") else None
    if not video:
        errors.append("missing_video_stream")
    if duration is None or duration <= 0:
        errors.append("zero_or_missing_duration")
    if width is not None and width <= 0:
        errors.append("invalid_width")
    if height is not None and height <= 0:
        errors.append("invalid_height")

    return MediaProbeReport(
        ok=not errors,
        path=path,
        size_bytes=size,
        duration_seconds=duration,
        width=width,
        height=height,
        video_codec=video.get("codec_name") if video else None,
        audio_codec=audio.get("codec_name") if audio else None,
        has_video=video is not None,
        has_audio=audio is not None,
        errors=errors,
        raw=raw,
    )


def assert_final_video_quality(path: str, *, expected_aspect_ratio: str | None = None, planned_duration_seconds: float | None = None) -> MediaProbeReport:
    report = ffprobe_media(path)
    errors = list(report.errors)
    if expected_aspect_ratio and report.width and report.height:
        target = expected_aspect_ratio.strip()
        ratios = {"16:9": 16 / 9, "9:16": 9 / 16, "1:1": 1.0}
        if target in ratios:
            actual = report.width / report.height
            if abs(actual - ratios[target]) > 0.08:
                errors.append(f"aspect_ratio_mismatch:{target}:{report.width}x{report.height}")
    if planned_duration_seconds and report.duration_seconds:
        tolerance = max(3.0, planned_duration_seconds * 0.15)
        if abs(report.duration_seconds - planned_duration_seconds) > tolerance:
            errors.append(f"duration_mismatch:planned={planned_duration_seconds}:actual={report.duration_seconds}")
    if errors:
        raise RenderArtifactError(f"final video quality gate failed: {errors}")
    return report
