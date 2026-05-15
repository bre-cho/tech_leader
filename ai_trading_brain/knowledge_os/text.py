from __future__ import annotations

import math
import re
from collections import Counter
from hashlib import blake2b
from typing import Iterable

TOKEN_RE = re.compile(r"[\wÀ-ỹ]+", re.UNICODE)

VI_STOPWORDS = {
    "và", "là", "của", "cho", "một", "các", "những", "để", "trong", "khi", "với",
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "is", "are", "on", "by"
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(normalize(text)) if t and t not in VI_STOPWORDS and len(t) > 1]


def chunk_text(text: str, max_words: int = 160, overlap: int = 35) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, max_words - overlap)
    for start in range(0, len(words), step):
        part = words[start:start + max_words]
        if part:
            chunks.append(" ".join(part))
        if start + max_words >= len(words):
            break
    return chunks


def hashed_vector(tokens: Iterable[str], dimensions: int = 256) -> list[float]:
    vec = [0.0] * dimensions
    counts = Counter(tokens)
    for token, count in counts.items():
        digest = blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vec[bucket] += sign * (1.0 + math.log(count))
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return max(0.0, sum(x * y for x, y in zip(a, b)))


def top_terms(text: str, limit: int = 12) -> list[str]:
    return [term for term, _ in Counter(tokenize(text)).most_common(limit)]
