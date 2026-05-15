from __future__ import annotations

import json
from pathlib import Path
from dataclasses import asdict

from .indexer import KnowledgeIndexer
from .rag import KnowledgeAssistant
from .search import HybridSearchEngine
from .store import KnowledgeStore


class KnowledgeOSRuntime:
    def __init__(self, db_path: str | Path = ".knowledge_os/knowledge.sqlite") -> None:
        self.store = KnowledgeStore(db_path)
        self.indexer = KnowledgeIndexer(self.store)
        self.search = HybridSearchEngine(self.store)
        self.assistant = KnowledgeAssistant(self.search)

    def build_index(self, root: str | Path = ".", reset: bool = True) -> dict:
        result = self.indexer.build(root=root, reset=reset)
        self.store.add_memory("index_build", json.dumps(result, ensure_ascii=False), score=float(result.get("chunks", 0)), metadata={"root": str(root)})
        return result

    def query(self, text: str, limit: int = 5) -> dict:
        ctx = self.assistant.answer(text, limit=limit)
        data = asdict(ctx)
        self.store.add_memory("query", text, score=ctx.confidence, metadata={"hits": len(ctx.hits)})
        return data

    def remember_winner(self, content: str, score: float, kind: str = "winner_pattern") -> dict:
        memory_id = self.store.add_memory(kind, content, score=score, metadata={"source": "knowledge_os"})
        return {"memory_id": memory_id, "kind": kind, "score": score, "content": content}

    def recall(self, kind: str | None = None, limit: int = 10) -> list[dict]:
        return self.store.memories(kind=kind, limit=limit)
