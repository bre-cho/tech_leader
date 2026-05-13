from __future__ import annotations

import os
import subprocess
from pathlib import Path


class FFmpegExecutionError(RuntimeError):
    pass


def ensure_file(path: str | Path, label: str) -> Path:
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"{label} not found: {p}")
    if p.stat().st_size <= 0:
        raise ValueError(f"{label} is empty: {p}")
    return p


def run_cmd(cmd: list[str], *, label: str, timeout: int | None = None) -> subprocess.CompletedProcess:
    timeout = timeout or int(os.getenv("FFMPEG_TIMEOUT_SEC", "600"))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise FFmpegExecutionError(
            f"{label} failed with code {result.returncode}\n"
            f"cmd: {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout[-2000:]}\n"
            f"stderr:\n{result.stderr[-4000:]}"
        )
    return result


def get_duration(path: str | Path) -> float:
    ensure_file(path, "media")
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    result = run_cmd(cmd, label="ffprobe duration", timeout=60)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 1.0
