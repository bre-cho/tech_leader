from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import KnowledgeChunk, SearchHit, GraphEdge


class KnowledgeStore:
    """SQLite-backed local-first knowledge store inspired by txtai's all-in-one idea."""

    def __init__(self, db_path: str | Path = ".knowledge_os/knowledge.sqlite") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                doc_id TEXT NOT NULL,
                path TEXT NOT NULL,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                position INTEGER NOT NULL,
                tokens TEXT NOT NULL,
                vector TEXT NOT NULL,
                metadata TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS edges (
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                weight REAL NOT NULL,
                relation TEXT NOT NULL,
                PRIMARY KEY(source, target, relation)
            );
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                content TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 0,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);
            CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source);
            CREATE INDEX IF NOT EXISTS idx_memories_kind ON memories(kind);
            """
        )
        self.conn.commit()

    def clear(self) -> None:
        self.conn.executescript("DELETE FROM chunks; DELETE FROM edges;")
        self.conn.commit()

    def upsert_chunks(self, rows: Iterable[tuple[KnowledgeChunk, list[str], list[float]]]) -> int:
        count = 0
        for chunk, tokens, vector in rows:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO chunks(chunk_id, doc_id, path, title, text, position, tokens, vector, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk.chunk_id,
                    chunk.doc_id,
                    chunk.path,
                    chunk.title,
                    chunk.text,
                    chunk.position,
                    json.dumps(tokens, ensure_ascii=False),
                    json.dumps(vector),
                    json.dumps(chunk.metadata, ensure_ascii=False),
                ),
            )
            count += 1
        self.conn.commit()
        return count

    def upsert_edges(self, edges: Iterable[GraphEdge]) -> int:
        count = 0
        for edge in edges:
            self.conn.execute(
                """
                INSERT INTO edges(source, target, weight, relation)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(source, target, relation)
                DO UPDATE SET weight = excluded.weight
                """,
                (edge.source, edge.target, edge.weight, edge.relation),
            )
            count += 1
        self.conn.commit()
        return count

    def chunks(self) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM chunks"))

    def related_terms(self, terms: Iterable[str]) -> dict[str, float]:
        scores: dict[str, float] = {}
        for term in terms:
            for row in self.conn.execute("SELECT target, weight FROM edges WHERE source = ?", (term,)):
                scores[row["target"]] = scores.get(row["target"], 0.0) + float(row["weight"])
        return scores

    def add_memory(self, kind: str, content: str, score: float = 0.0, metadata: dict | None = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO memories(kind, content, score, metadata) VALUES (?, ?, ?, ?)",
            (kind, content, score, json.dumps(metadata or {}, ensure_ascii=False)),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def memories(self, kind: str | None = None, limit: int = 20) -> list[dict]:
        if kind:
            rows = self.conn.execute(
                "SELECT * FROM memories WHERE kind = ? ORDER BY score DESC, id DESC LIMIT ?", (kind, limit)
            )
        else:
            rows = self.conn.execute("SELECT * FROM memories ORDER BY score DESC, id DESC LIMIT ?", (limit,))
        return [dict(row) | {"metadata": json.loads(row["metadata"])} for row in rows]
