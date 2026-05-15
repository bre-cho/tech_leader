from __future__ import annotations

import json
import math
from collections import Counter

from .models import SearchHit
from .store import KnowledgeStore
from .text import cosine, hashed_vector, tokenize


class HybridSearchEngine:
    def __init__(self, store: KnowledgeStore) -> None:
        self.store = store

    def _idf(self, rows: list, query_terms: list[str]) -> dict[str, float]:
        total = max(1, len(rows))
        result: dict[str, float] = {}
        for term in set(query_terms):
            docs = sum(1 for row in rows if term in set(json.loads(row["tokens"])))
            result[term] = math.log((total + 1) / (docs + 1)) + 1.0
        return result

    def search(self, query: str, limit: int = 5) -> list[SearchHit]:
        rows = self.store.chunks()
        q_tokens = tokenize(query)
        q_vector = hashed_vector(q_tokens)
        idf = self._idf(rows, q_tokens)
        related = self.store.related_terms(q_tokens)
        max_related = max(related.values(), default=1.0)
        hits: list[SearchHit] = []
        for row in rows:
            tokens = json.loads(row["tokens"])
            counts = Counter(tokens)
            lexical = sum((1 + math.log(counts[t])) * idf.get(t, 1.0) for t in set(q_tokens) if counts.get(t))
            semantic = cosine(q_vector, json.loads(row["vector"]))
            graph = sum(related.get(t, 0.0) for t in set(tokens)) / max_related if related else 0.0
            score = lexical * 0.55 + semantic * 0.35 + graph * 0.10
            if score > 0:
                hits.append(
                    SearchHit(
                        chunk_id=row["chunk_id"],
                        doc_id=row["doc_id"],
                        path=row["path"],
                        title=row["title"],
                        text=row["text"],
                        score=round(score, 6),
                        lexical_score=round(lexical, 6),
                        semantic_score=round(semantic, 6),
                        graph_score=round(graph, 6),
                        metadata=json.loads(row["metadata"]),
                    )
                )
        return sorted(hits, key=lambda h: h.score, reverse=True)[:limit]
