from __future__ import annotations

import re
from typing import List, Optional

from app.video_postprocess.contracts import SubtitleEmotion, SubtitleLine, WordTiming


_WORD_RE = re.compile(r"\S+")


def _keyword_flags(word: str) -> bool:
    hot = {
        "sale", "new", "hot", "free", "giảm", "mới", "đẹp", "trắng", "glow",
        "luxury", "premium", "khuyến", "mại", "nhanh", "ngay"
    }
    return word.lower().strip(".,!?").replace("🔥", "") in hot


def build_word_timestamps_from_script(script: str, duration: float) -> List[WordTiming]:
    words = [m.group(0) for m in _WORD_RE.finditer(script)]
    if not words:
        return []
    avg = max(duration / len(words), 0.18)
    timings = []
    t = 0.0
    for word in words:
        end = min(t + avg, duration)
        timings.append(WordTiming(word=word, start=round(t, 3), end=round(end, 3), emphasis=_keyword_flags(word)))
        t = end
    return timings


def build_subtitle_lines(
    *,
    script: str,
    duration: float,
    max_chars: int,
    max_words_per_line: int,
    scene_id: str | None,
    emotion: SubtitleEmotion,
    real_word_timestamps: Optional[List[WordTiming]] = None,
) -> List[SubtitleLine]:
    words = real_word_timestamps or build_word_timestamps_from_script(script, duration)
    lines: List[SubtitleLine] = []

    bucket: List[WordTiming] = []
    chars = 0
    idx = 1

    for word in words:
        new_chars = chars + len(word.word) + (1 if bucket else 0)
        if bucket and (new_chars > max_chars or len(bucket) >= max_words_per_line):
            lines.append(_line(idx, bucket, scene_id, emotion))
            idx += 1
            bucket = []
            chars = 0
        bucket.append(word)
        chars += len(word.word) + (1 if bucket else 0)

    if bucket:
        lines.append(_line(idx, bucket, scene_id, emotion))

    return lines


def _line(idx: int, words: List[WordTiming], scene_id: str | None, emotion: SubtitleEmotion) -> SubtitleLine:
    text = " ".join(w.word for w in words)
    return SubtitleLine(
        line_id=f"sub_{idx:03d}",
        text=text,
        start=words[0].start,
        end=words[-1].end,
        words=words,
        scene_id=scene_id,
        emotion=emotion,
        keywords=[w.word for w in words if w.emphasis],
    )
