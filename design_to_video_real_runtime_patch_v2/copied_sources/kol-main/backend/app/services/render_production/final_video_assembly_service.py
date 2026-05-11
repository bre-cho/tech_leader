from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from .contracts import RenderProductionError, ensure_file
from .ffmpeg_utils import run_cmd


class FinalVideoAssemblyService:
    """Normalize and concatenate scene MP4s into one final raw video."""

    def normalize_scene(
        self,
        *,
        input_path: str,
        output_path: str,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
    ) -> str:
        ensure_file(input_path, "scene video")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
        )
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", vf,
            "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", output_path,
        ]
        run_cmd(cmd, label="normalize scene")
        ensure_file(output_path, "normalized scene")
        return output_path

    def assemble(
        self,
        *,
        scene_video_paths: Iterable[str],
        output_path: str,
        work_dir: str,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
    ) -> str:
        paths = list(scene_video_paths)
        if not paths:
            raise RenderProductionError("No scene videos provided for final assembly")
        work = Path(work_dir)
        norm_dir = work / "normalized_scenes"
        norm_dir.mkdir(parents=True, exist_ok=True)
        normalized: List[str] = []
        for idx, p in enumerate(paths, start=1):
            normalized.append(self.normalize_scene(input_path=p, output_path=str(norm_dir / f"scene_{idx:03d}.mp4"), width=width, height=height, fps=fps))

        concat_file = work / "concat.txt"
        concat_file.write_text("\n".join(f"file '{Path(p).resolve().as_posix()}'" for p in normalized), encoding="utf-8")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c", "copy", output_path,
        ]
        run_cmd(cmd, label="concat scenes")
        ensure_file(output_path, "assembled video")
        return output_path
