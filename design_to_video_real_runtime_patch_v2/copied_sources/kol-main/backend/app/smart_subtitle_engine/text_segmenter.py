from __future__ import annotations

import re
from typing import Iterable, List

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+|\n+")


def normalize_script(script: str) -> str:
    script = re.sub(r"\s+", " ", script or "").strip()
    return script


def split_into_lines(script: str, max_chars: int = 26) -> List[str]:
    """Split narration into subtitle-friendly lines without losing words."""
    script = normalize_script(script)
    if not script:
        return []
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(script) if s.strip()]
    lines: List[str] = []
    for sentence in sentences:
        words = sentence.split()
        current: List[str] = []
        for word in words:
            candidate = " ".join([*current, word]).strip()
            if current and len(candidate) > max_chars:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
    return lines


def extract_keywords(text: str) -> List[str]:
    words = re.findall(r"[A-Za-zÀ-ỹ0-9']+", text or "")
    stop = {"the", "and", "with", "that", "this", "you", "your", "for", "một", "và", "của", "là", "để", "cho"}
    ranked = [w for w in words if len(w) >= 5 and w.lower() not in stop]
    return ranked[:3]
