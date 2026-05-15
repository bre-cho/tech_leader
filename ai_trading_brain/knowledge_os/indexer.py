from __future__ import annotations

from collections import Counter
from pathlib import Path

from .models import KnowledgeChunk, GraphEdge, safe_doc_id
from .store import KnowledgeStore
from .text import chunk_text, hashed_vector, tokenize, top_terms

TEXT_SUFFIXES = {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".toml", ".csv"}
IGNORE_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "dist", "build", ".venv", "venv"}


class KnowledgeIndexer:
    def __init__(self, store: KnowledgeStore) -> None:
        self.store = store

    def scan_files(self, root: str | Path, max_files: int = 500) -> list[Path]:
        root = Path(root)
        files: list[Path] = []
        for path in root.rglob("*"):
            if len(files) >= max_files:
                break
            if any(part in IGNORE_DIRS for part in path.parts):
                continue
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                try:
                    if path.stat().st_size <= 750_000:
                        files.append(path)
                except OSError:
                    continue
        return files

    def build(self, root: str | Path, reset: bool = True) -> dict:
        if reset:
            self.store.clear()
        files = self.scan_files(root)
        chunk_rows = []
        all_edges: Counter[tuple[str, str]] = Counter()
        for file_path in files:
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            doc_id = safe_doc_id(file_path)
            title = file_path.name
            for pos, chunk_text_value in enumerate(chunk_text(text)):
                tokens = tokenize(chunk_text_value)
                vector = hashed_vector(tokens)
                chunk = KnowledgeChunk(
                    chunk_id=f"{doc_id}:{pos}",
                    doc_id=doc_id,
                    path=str(file_path),
                    title=title,
                    text=chunk_text_value,
                    position=pos,
                    metadata={"suffix": file_path.suffix.lower()},
                )
                chunk_rows.append((chunk, tokens, vector))
                terms = top_terms(chunk_text_value, 8)
                for i, source in enumerate(terms):
                    for target in terms[i + 1:]:
                        if source != target:
                            all_edges[(source, target)] += 1
                            all_edges[(target, source)] += 1
        chunks = self.store.upsert_chunks(chunk_rows)
        edges = self.store.upsert_edges(
            GraphEdge(source=s, target=t, weight=float(w)) for (s, t), w in all_edges.items()
        )
        return {"files": len(files), "chunks": chunks, "edges": edges, "db_path": str(self.store.db_path)}
