from __future__ import annotations

from pathlib import Path
from typing import Optional

from .contracts import ensure_file
from .ffmpeg_utils import run_cmd


class RealSubtitleBurnService:
    """Burn ASS/SRT subtitles and attach final audio."""

    def burn(
        self,
        *,
        video_path: str,
        output_path: str,
        subtitle_path: Optional[str] = None,
        audio_path: Optional[str] = None,
    ) -> str:
        ensure_file(video_path, "video before subtitle burn")
        if subtitle_path:
            ensure_file(subtitle_path, "subtitle file")
        if audio_path:
            ensure_file(audio_path, "final audio")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cmd = ["ffmpeg", "-y", "-i", video_path]
        if audio_path:
            cmd += ["-i", audio_path]

        vf = []
        if subtitle_path:
            escaped = str(Path(subtitle_path)).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
            vf.append(f"subtitles='{escaped}'")

        if vf:
            cmd += ["-vf", ",".join(vf)]
        if audio_path:
            cmd += ["-map", "0:v:0", "-map", "1:a:0"]
        else:
            cmd += ["-map", "0:v:0", "-map", "0:a?", "-shortest"]

        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path]
        run_cmd(cmd, label="subtitle burn / mux")
        ensure_file(output_path, "final video")
        return output_path
