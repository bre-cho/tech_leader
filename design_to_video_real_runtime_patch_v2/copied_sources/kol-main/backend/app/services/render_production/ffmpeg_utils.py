from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .contracts import RenderProductionError


def run_cmd(cmd: List[str], *, label: str = "command", timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, check=True, text=True, capture_output=True, timeout=timeout)
    except subprocess.CalledProcessError as e:
        pretty = " ".join(shlex.quote(x) for x in cmd)
        raise RenderProductionError(
            f"{label} failed\nCMD: {pretty}\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
        ) from e


def ffprobe_json(path: str | Path) -> Dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    result = run_cmd(cmd, label="ffprobe")
    return json.loads(result.stdout or "{}")


def get_duration(path: str | Path) -> float:
    data = ffprobe_json(path)
    duration = data.get("format", {}).get("duration")
    try:
        return float(duration)
    except Exception:
        return 0.0


def video_stream_info(path: str | Path) -> Dict[str, Any]:
    data = ffprobe_json(path)
    for s in data.get("streams", []):
        if s.get("codec_type") == "video":
            return s
    raise RenderProductionError(f"No video stream found: {path}")


def audio_stream_info(path: str | Path) -> Optional[Dict[str, Any]]:
    data = ffprobe_json(path)
    for s in data.get("streams", []):
        if s.get("codec_type") == "audio":
            return s
    return None


def assert_aspect_ratio(path: str | Path, expected: str = "9:16", tolerance: float = 0.03) -> None:
    info = video_stream_info(path)
    w, h = int(info.get("width", 0)), int(info.get("height", 0))
    if not w or not h:
        raise RenderProductionError(f"Cannot read video dimensions: {path}")
    left, right = expected.split(":")
    expected_ratio = float(left) / float(right)
    actual = w / h
    if abs(actual - expected_ratio) > tolerance:
        raise RenderProductionError(f"Aspect ratio mismatch: got {w}:{h}, expected {expected}")
