from __future__ import annotations

from typing import List, Optional
from .schemas import SubtitleIntensity, SubtitleLine, WordTiming
from .text_segmenter import extract_keywords, split_into_lines


PACE_BY_EMOTION = {
    SubtitleIntensity.asmr: 0.52,
    SubtitleIntensity.documentary: 0.43,
    SubtitleIntensity.luxury: 0.38,
    SubtitleIntensity.calm: 0.40,
    SubtitleIntensity.dramatic: 0.34,
    SubtitleIntensity.viral: 0.30,
}


def build_subtitle_lines(
    script: str,
    duration: float,
    max_chars: int,
    scene_id: str | None,
    emotion: SubtitleIntensity,
    real_word_timestamps: Optional[List[WordTiming]] = None,
) -> List[SubtitleLine]:
    lines = split_into_lines(script, max_chars=max_chars)
    if not lines:
        return []

    if real_word_timestamps:
        return _lines_from_real_word_timing(lines, real_word_timestamps, scene_id, emotion)

    total_words = sum(max(1, len(line.split())) for line in lines)
    seconds_per_word = max(duration / max(total_words, 1), PACE_BY_EMOTION.get(emotion, 0.38))
    current = 0.0
    subtitle_lines: List[SubtitleLine] = []
    for idx, text in enumerate(lines, start=1):
        words = text.split()
        line_duration = min(max(1.05, len(words) * seconds_per_word), 3.2)
        start = current
        end = min(duration, start + line_duration)
        if end <= start:
            end = start + 0.8
        word_timings: List[WordTiming] = []
        step = (end - start) / max(len(words), 1)
        keywords = [k.lower() for k in extract_keywords(text)]
        for word_index, word in enumerate(words):
            clean = word.strip(".,!?;:()[]{}\"'").lower()
            word_timings.append(
                WordTiming(
                    word=word,
                    start=round(start + word_index * step, 3),
                    end=round(start + (word_index + 1) * step, 3),
                    confidence=0.82,
                    emphasis=clean in keywords,
                )
            )
        subtitle_lines.append(
            SubtitleLine(
                line_id=f"{scene_id or 'scene'}_sub_{idx:03d}",
                text=text,
                start=round(start, 3),
                end=round(end, 3),
                words=word_timings,
                scene_id=scene_id,
                emotion=emotion,
                keywords=extract_keywords(text),
            )
        )
        current = end + 0.08
        if current >= duration:
            break
    return subtitle_lines


def _lines_from_real_word_timing(
    lines: List[str],
    word_timings: List[WordTiming],
    scene_id: str | None,
    emotion: SubtitleIntensity,
) -> List[SubtitleLine]:
    cursor = 0
    result: List[SubtitleLine] = []
    for idx, text in enumerate(lines, start=1):
        word_count = len(text.split())
        chunk = word_timings[cursor : cursor + word_count]
        cursor += word_count
        if not chunk:
            continue
        result.append(
            SubtitleLine(
                line_id=f"{scene_id or 'scene'}_sub_{idx:03d}",
                text=text,
                start=chunk[0].start,
                end=chunk[-1].end,
                words=chunk,
                scene_id=scene_id,
                emotion=emotion,
                keywords=extract_keywords(text),
            )
        )
    return result
