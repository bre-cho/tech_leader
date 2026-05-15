from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class KnowledgeDocument:
    doc_id: str
    path: str
    title: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    doc_id: str
    path: str
    title: str
    text: str
    position: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchHit:
    chunk_id: str
    doc_id: str
    path: str
    title: str
    text: str
    score: float
    lexical_score: float
    semantic_score: float
    graph_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AnswerContext:
    query: str
    answer: str
    hits: list[SearchHit]
    citations: list[str]
    confidence: float


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    weight: float
    relation: str = "co_occurs_with"


def to_dict(obj: Any) -> dict[str, Any]:
    return asdict(obj)


def safe_doc_id(path: str | Path) -> str:
    p = str(path).replace('\\', '/')
    return ''.join(ch if ch.isalnum() else '_' for ch in p).strip('_')[:180]
