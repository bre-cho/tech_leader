import logging
import os
import subprocess
from pathlib import Path
from typing import Sequence

from app.core.config import settings

_logger = logging.getLogger(__name__)


def build_concat_file(paths: Sequence[str], workdir: Path) -> Path:
    concat_file = workdir / "concat.txt"
    concat_file.write_text("\n".join([f"file '{Path(p).as_posix()}'" for p in paths]), encoding="utf-8")
    return concat_file


def _normalize_clips(paths: Sequence[str], workdir: Path) -> list[str]:
    """Re-encode each clip to a common H.264/AAC baseline before concat.

    This eliminates timebase, codec, or frame-size mismatches that cause the
    copy-mode concat demuxer to produce a corrupt or unplayable output.  The
    normalized files are written to *workdir* and the paths returned.

    This step is intentionally skipped when all input files share the same
    codec/timebase (the common case) — see ``merge_clips_concat`` which tries
    copy-mode first and only calls this on failure.
    """
    ffmpeg = settings.ffmpeg_binary
    timeout = int(os.getenv("FFMPEG_NORMALIZE_TIMEOUT_SEC", "600"))
    normalized: list[str] = []
    for idx, src in enumerate(paths):
        dst = str(workdir / f"norm_{idx:04d}.mp4")
        try:
            result = subprocess.run(
                [
                    ffmpeg, "-y", "-i", src,
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-ar", "44100", "-ac", "2",
                    "-movflags", "+faststart",
                    dst,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"Codec normalization timed out after {timeout}s for clip {src}"
            ) from exc
        if result.returncode != 0:
            raise RuntimeError(f"Codec normalization failed for {src}: {result.stderr[-2000:]}")
        normalized.append(dst)
    return normalized


def merge_clips_concat(paths: Sequence[str], output_path: str) -> str:
    """Merge *paths* into *output_path* using the FFmpeg concat demuxer.

    Strategy:
    1. Try stream-copy concat (fast, no re-encode).
    2. If that fails (mismatched codecs/timebase), normalize all inputs to a
       common H.264/AAC baseline and retry the copy-mode concat.

    This matches the two-stage approach used by
    :func:`~app.services.render_artifact_service.run_ffmpeg_concat` to ensure
    mixed-timebase clips from multiple Veo requests can always be merged.
    """
    workdir = Path(output_path).parent
    workdir.mkdir(parents=True, exist_ok=True)
    concat_file = build_concat_file(paths, workdir)
    timeout = int(os.getenv("FFMPEG_NORMALIZE_TIMEOUT_SEC", "600"))

    result = subprocess.run(
        [settings.ffmpeg_binary, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", output_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    if result.returncode == 0:
        return output_path

    # Copy-mode failed — normalize clips to a common codec/timebase and retry.
    _logger.warning(
        "merge_clips_concat: copy-mode concat failed (returncode=%d); "
        "normalizing clips to H.264/AAC and retrying. stderr=%s",
        result.returncode,
        result.stderr[-1000:],
    )
    normalized = _normalize_clips(paths, workdir)
    norm_concat = build_concat_file(normalized, workdir)
    try:
        subprocess.run(
            [settings.ffmpeg_binary, "-y", "-f", "concat", "-safe", "0", "-i", str(norm_concat), "-c", "copy", output_path],
            check=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"merge_clips_concat final concat timed out after {timeout}s"
        ) from exc
    return output_path
