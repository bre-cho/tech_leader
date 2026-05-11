"""RAG retrieval service — TF-IDF or OpenRouter embeddings backend.

Backends
--------
``RAG_EMBEDDING_BACKEND=tfidf`` (default)
    Pure-Python TF-IDF retrieval built on the stdlib only.  No ML
    dependencies required.  Suitable for small-to-medium doc corpora.
    The index is built once on first call and persisted to
    ``RAG_VECTOR_STORE_PATH`` (JSON) so subsequent worker starts skip
    re-indexing unless the docs root changes.

``RAG_EMBEDDING_BACKEND=openrouter``
    Uses the OpenRouter /embeddings endpoint to produce dense vectors.
    Requires ``OPENROUTER_API_KEY`` and ``httpx``.
    Falls back to TF-IDF when the API key is absent or the call fails,
    so the service never raises in dev/CI environments.

Index management
----------------
``build_index()``       — (re)build and persist the index.
``retrieve_and_assemble(query, top_k)`` — public entry point used by
    ``llm_client.chat_with_rag()``.  Auto-builds the index on first call.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import httpx as _httpx
except ImportError:  # httpx is a required dep but guard for test isolation
    _httpx = None  # type: ignore[assignment]

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy settings import to avoid circular dependency at module load time.
# ---------------------------------------------------------------------------


def _settings():
    from app.core.config import settings as _s  # noqa: PLC0415
    return _s


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class RetrievedChunk:
    """A retrieved document chunk with metadata."""

    source: str
    text: str
    score: float = 0.0


@dataclass
class _TfIdfIndex:
    """In-process TF-IDF index.

    Attributes
    ----------
    chunks     : flat list of ``RetrievedChunk`` (no score yet).
    idf        : IDF weight per unique term.
    tfidf_vecs : TF-IDF vectors, one per chunk (term → float dict).
    doc_hash   : SHA-256 of the serialised index; used for cache validation.
    """

    chunks: list[RetrievedChunk] = field(default_factory=list)
    idf: dict[str, float] = field(default_factory=dict)
    tfidf_vecs: list[dict[str, float]] = field(default_factory=list)
    doc_hash: str = ""


# Module-level singleton — built lazily and protected by a lock so multiple
# workers / threads only build the index once.
_INDEX: _TfIdfIndex | None = None
_INDEX_LOCK = threading.Lock()

# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[a-zA-Z0-9']+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _tf(tokens: list[str]) -> dict[str, float]:
    """Term frequency (raw count / total)."""
    total = max(len(tokens), 1)
    freq: dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    return {t: c / total for t, c in freq.items()}


def _idf(docs: list[list[str]]) -> dict[str, float]:
    """Inverse document frequency: log((N+1)/(df+1)) + 1 (smoothed)."""
    n = len(docs)
    df: dict[str, int] = {}
    for doc in docs:
        for t in set(doc):
            df[t] = df.get(t, 0) + 1
    return {t: math.log((n + 1) / (count + 1)) + 1.0 for t, count in df.items()}


def _tfidf_vec(tf_map: dict[str, float], idf_map: dict[str, float]) -> dict[str, float]:
    return {t: w * idf_map.get(t, 1.0) for t, w in tf_map.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) & set(b)
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a < 1e-12 or norm_b < 1e-12:
        return 0.0
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Document loading & chunking
# ---------------------------------------------------------------------------


def _load_docs(docs_root: str) -> list[tuple[str, str]]:
    """Recursively load all Markdown/text files under *docs_root*.

    Returns a list of ``(source_path, text)`` tuples.
    """
    root = Path(docs_root)
    if not root.exists():
        _logger.warning("RAG docs_root does not exist: %s — index will be empty", docs_root)
        return []

    results: list[tuple[str, str]] = []
    for ext in ("*.md", "*.txt", "*.rst"):
        for path in root.rglob(ext):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                results.append((str(path), text))
            except OSError as exc:
                _logger.warning("Could not read %s: %s", path, exc)
    return results


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split *text* into overlapping word-chunks of *chunk_size* words."""
    words = text.split()
    step = max(chunk_size - overlap, 1)
    chunks = []
    for i in range(0, max(len(words), 1), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


# ---------------------------------------------------------------------------
# Index persistence (JSON)
# ---------------------------------------------------------------------------


def _persist_index(index: _TfIdfIndex, path: str) -> None:
    try:
        data = {
            "doc_hash": index.doc_hash,
            "idf": index.idf,
            "chunks": [
                {"source": c.source, "text": c.text}
                for c in index.chunks
            ],
            "tfidf_vecs": index.tfidf_vecs,
        }
        tmp = path + ".tmp"
        Path(tmp).parent.mkdir(parents=True, exist_ok=True)
        Path(tmp).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)
    except OSError as exc:
        _logger.warning("Could not persist RAG index to %s: %s", path, exc)


def _load_persisted_index(path: str) -> _TfIdfIndex | None:
    try:
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
        chunks = [
            RetrievedChunk(source=c["source"], text=c["text"])
            for c in data.get("chunks", [])
        ]
        return _TfIdfIndex(
            chunks=chunks,
            idf=data.get("idf", {}),
            tfidf_vecs=data.get("tfidf_vecs", []),
            doc_hash=data.get("doc_hash", ""),
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return None


def _docs_hash(docs: list[tuple[str, str]]) -> str:
    h = hashlib.sha256()
    for src, text in sorted(docs, key=lambda x: x[0]):
        h.update(src.encode())
        h.update(text.encode())
    return h.hexdigest()


# ---------------------------------------------------------------------------
# TF-IDF index builder
# ---------------------------------------------------------------------------


def _build_tfidf_index(docs_root: str, chunk_size: int, overlap: int) -> _TfIdfIndex:
    """Build a TF-IDF index over all docs under *docs_root*."""
    raw_docs = _load_docs(docs_root)
    current_hash = _docs_hash(raw_docs)

    # Build chunks
    chunks: list[RetrievedChunk] = []
    for source, text in raw_docs:
        for chunk in _chunk_text(text, chunk_size, overlap):
            chunks.append(RetrievedChunk(source=source, text=chunk))

    if not chunks:
        _logger.warning("RAG index is empty — no documents found under %s", docs_root)
        return _TfIdfIndex(doc_hash=current_hash)

    # Tokenise
    tokenised = [_tokenize(c.text) for c in chunks]
    idf_map = _idf(tokenised)
    tfidf_vecs = [_tfidf_vec(_tf(tok), idf_map) for tok in tokenised]

    return _TfIdfIndex(
        chunks=chunks,
        idf=idf_map,
        tfidf_vecs=tfidf_vecs,
        doc_hash=current_hash,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_index() -> None:
    """(Re)build the TF-IDF index and persist it to ``RAG_VECTOR_STORE_PATH``.

    Called explicitly to force a full rebuild, e.g. after docs are updated.
    Normal callers use :func:`retrieve_and_assemble`, which auto-builds lazily.
    """
    s = _settings()
    idx = _build_tfidf_index(s.rag_docs_root, s.rag_chunk_size, s.rag_chunk_overlap)
    _persist_index(idx, s.rag_vector_store_path)
    set_index(idx)
    _logger.info(
        "RAG index built: %d chunks from %s",
        len(idx.chunks),
        s.rag_docs_root,
    )


def set_index(idx: _TfIdfIndex) -> None:
    """Replace the in-process cached index with *idx*.

    Acquires ``_INDEX_LOCK`` so concurrent workers see a consistent value.
    Use this instead of directly mutating the module-level ``_INDEX`` variable.
    """
    global _INDEX  # noqa: PLW0603
    with _INDEX_LOCK:
        _INDEX = idx


_HASH_DISPLAY_LENGTH: int = 12  # chars of SHA-256 hash to log for readability


def _get_or_build_index() -> _TfIdfIndex:
    """Return the in-process index, building it if necessary.

    Staleness check: when a persisted index is loaded its ``doc_hash`` is
    compared against the current docs on disk.  If the docs have changed
    (files added, removed, or modified) the index is rebuilt automatically
    so queries always reflect the latest documentation without requiring a
    manual ``build_index()`` call.
    """
    global _INDEX  # noqa: PLW0603
    with _INDEX_LOCK:
        if _INDEX is not None:
            return _INDEX

        s = _settings()
        # Try loading persisted index first
        persisted = _load_persisted_index(s.rag_vector_store_path)
        if persisted and persisted.chunks:
            # Staleness check — compare the stored hash against the current docs.
            current_docs = _load_docs(s.rag_docs_root)
            current_hash = _docs_hash(current_docs)
            if persisted.doc_hash and persisted.doc_hash == current_hash:
                _logger.debug("RAG: loaded persisted index (%d chunks)", len(persisted.chunks))
                _INDEX = persisted
                return _INDEX
            _logger.info(
                "RAG: persisted index is stale (stored_hash=%s, current_hash=%s); rebuilding",
                persisted.doc_hash[:_HASH_DISPLAY_LENGTH] if persisted.doc_hash else "none",
                current_hash[:_HASH_DISPLAY_LENGTH],
            )

        # Build fresh (either no persisted index or it was stale)
        _logger.info("RAG: building TF-IDF index from %s", s.rag_docs_root)
        idx = _build_tfidf_index(s.rag_docs_root, s.rag_chunk_size, s.rag_chunk_overlap)
        _persist_index(idx, s.rag_vector_store_path)
        _INDEX = idx
        return _INDEX


def retrieve_and_assemble(
    query: str,
    *,
    top_k: int | None = None,
) -> tuple[list[RetrievedChunk], str]:
    """Retrieve the top-K most relevant chunks for *query* and assemble context.

    Parameters
    ----------
    query   : Natural-language query string.
    top_k   : Number of chunks to return.  Defaults to ``settings.rag_top_k``.

    Returns
    -------
    ``(chunks, context_str)`` where *context_str* is a formatted string
    ready for injection into the LLM system prompt.  ``context_str`` is
    empty when ``RAG_ENABLED=false`` or the index is empty.
    """
    s = _settings()
    if not s.rag_enabled:
        return [], ""

    k = top_k if top_k is not None else s.rag_top_k
    backend = s.rag_embedding_backend.lower().strip()

    if backend == "openrouter":
        try:
            return _openrouter_retrieve(query, top_k=k)
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "RAG OpenRouter retrieval failed (%s); falling back to TF-IDF", exc
            )

    return _tfidf_retrieve(query, top_k=k)


# ---------------------------------------------------------------------------
# TF-IDF retrieval
# ---------------------------------------------------------------------------


def _tfidf_retrieve(query: str, *, top_k: int) -> tuple[list[RetrievedChunk], str]:
    idx = _get_or_build_index()
    if not idx.chunks:
        return [], ""

    q_tokens = _tokenize(query)
    q_tfidf = _tfidf_vec(_tf(q_tokens), idx.idf)

    scored: list[tuple[float, int]] = []
    for i, vec in enumerate(idx.tfidf_vecs):
        score = _cosine(q_tfidf, vec)
        scored.append((score, i))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    results: list[RetrievedChunk] = []
    for score, i in top:
        c = idx.chunks[i]
        results.append(RetrievedChunk(source=c.source, text=c.text, score=score))

    context_str = _format_context(results)
    return results, context_str


# ---------------------------------------------------------------------------
# OpenRouter embeddings retrieval
# ---------------------------------------------------------------------------


def _embed_chunks_batched(
    api_key: str,
    model: str,
    chunk_texts: list[str],
    *,
    batch_size: int = 500,
) -> list[list[float]]:
    """Embed *chunk_texts* in batches of *batch_size* to avoid API request limits.

    OpenRouter's /embeddings endpoint accepts up to 500 inputs per request.
    Splitting into batches ensures all chunks are embedded even for large corpora
    instead of silently truncating to the first batch.
    """
    all_vecs: list[list[float]] = []
    for start in range(0, len(chunk_texts), batch_size):
        batch = chunk_texts[start : start + batch_size]
        resp = _httpx.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "input": batch},
            timeout=60,
        )
        resp.raise_for_status()
        all_vecs.extend(d["embedding"] for d in resp.json()["data"])
    return all_vecs


def _openrouter_retrieve(query: str, *, top_k: int) -> tuple[list[RetrievedChunk], str]:
    """Retrieve using dense embeddings via OpenRouter /embeddings."""
    s = _settings()
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    idx = _get_or_build_index()
    if not idx.chunks:
        return [], ""

    # Embed the query
    resp = _httpx.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": s.rag_embedding_model, "input": query},
        timeout=30,
    )
    resp.raise_for_status()
    q_vec: list[float] = resp.json()["data"][0]["embedding"]

    # Score all chunks using dot-product (embeddings are normalised by OpenRouter).
    # Chunks are embedded in batches of 500 so large corpora are fully covered
    # instead of being truncated to the first batch.
    chunk_texts = [c.text for c in idx.chunks]
    _BATCH_SIZE = 500
    if len(chunk_texts) > _BATCH_SIZE:
        _logger.info(
            "RAG OpenRouter: embedding %d chunks in batches of %d",
            len(chunk_texts),
            _BATCH_SIZE,
        )
    chunk_vecs = _embed_chunks_batched(api_key, s.rag_embedding_model, chunk_texts, batch_size=_BATCH_SIZE)

    def _dot(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    scored = sorted(
        enumerate(_dot(q_vec, cv) for cv in chunk_vecs),
        key=lambda x: x[1],
        reverse=True,
    )

    results = [
        RetrievedChunk(source=idx.chunks[i].source, text=idx.chunks[i].text, score=sc)
        for i, sc in scored[:top_k]
    ]
    return results, _format_context(results)


# ---------------------------------------------------------------------------
# Context assembly
# ---------------------------------------------------------------------------


def _format_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return ""
    parts: list[str] = []
    for idx, chunk in enumerate(chunks, 1):
        parts.append(
            f"[{idx}] Source: {chunk.source}\n{chunk.text.strip()}"
        )
    return "\n\n---\n\n".join(parts)
