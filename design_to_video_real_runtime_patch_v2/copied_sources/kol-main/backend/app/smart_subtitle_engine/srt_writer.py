from __future__ import annotations

from typing import List
from .schemas import SubtitleLine


def seconds_to_srt_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_srt(lines: List[SubtitleLine]) -> str:
    chunks = []
    for idx, line in enumerate(lines, start=1):
        chunks.append(f"{idx}\n{seconds_to_srt_time(line.start)} --> {seconds_to_srt_time(line.end)}\n{line.text}\n")
    return "\n".join(chunks)
