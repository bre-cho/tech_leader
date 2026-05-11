import os
import subprocess
from pathlib import Path
from typing import Sequence

from app.core.config import settings


def format_srt_ts(value: float) -> str:
    total_ms = int(round(value * 1000))
    hours = total_ms // 3600000
    total_ms %= 3600000
    minutes = total_ms // 60000
    total_ms %= 60000
    seconds = total_ms // 1000
    milliseconds = total_ms % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def _escape_subtitle_filter_path(path: str) -> str:
    """Escape a file path for use inside an FFmpeg ``subtitles=`` video filter.

    FFmpeg's filtergraph parser treats ``\\`` as an escape prefix and ``:``
    as an option separator, so both must be escaped before embedding a path
    in ``-vf subtitles=<path>``.  This mirrors the escaping done by
    :class:`~app.render.assembly.executors.ffmpeg_command_builder.FFmpegCommandBuilder`
    for ASS paths.
    """
    return path.replace("\\", "\\\\").replace(":", "\\:")


def write_srt(segments: Sequence[dict], output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, seg in enumerate(segments, start=1):
        lines += [str(i), f"{format_srt_ts(seg['start_sec'])} --> {format_srt_ts(seg['end_sec'])}", seg["text"], ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    return str(out)


def burn_subtitles(video_path: str, srt_path: str, output_path: str) -> str:
    """Burn *srt_path* subtitle track into *video_path*, writing to *output_path*.

    Uses FFmpeg's ``subtitles=`` video filter.  The SRT path is escaped so
    that colons and backslashes (e.g. Windows drive letters, paths with special
    characters) do not break the filtergraph parser.

    The subprocess is bounded by ``FFMPEG_BURN_TIMEOUT_SEC`` (default 600 s).
    A :class:`subprocess.TimeoutExpired` exception is converted to a
    :class:`RuntimeError` so Celery workers can retry rather than hanging.
    """
    timeout = int(os.getenv("FFMPEG_BURN_TIMEOUT_SEC", "600"))
    escaped = _escape_subtitle_filter_path(srt_path)
    try:
        subprocess.run(
            [settings.ffmpeg_binary, "-y", "-i", video_path, "-vf", f"subtitles={escaped}", output_path],
            check=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"burn_subtitles timed out after {timeout}s for video={video_path}"
        ) from exc
    return output_path
