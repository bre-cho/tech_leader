"""Celery worker: scheduled RAG index rebuild.

Registered as a Celery beat task (``rag.rebuild_index``) that fires every
``RAG_INDEX_REBUILD_INTERVAL_SECONDS`` (default 3600 s = 1 hour).

The task is a no-op when ``RAG_ENABLED=false`` so it does not waste CPU in
environments that do not use RAG.

On each run it computes the current SHA-256 hash of all documents in
``RAG_DOCS_ROOT``.  If the hash matches the persisted index the rebuild is
skipped, so the task is cheap when docs have not changed.

Route: ``rag`` queue (falls back to the ``celery`` default queue).
"""
from __future__ import annotations

import logging

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="rag.rebuild_index", bind=True, max_retries=2, default_retry_delay=60)
def rebuild_rag_index(self) -> dict:  # type: ignore[override]
    """Rebuild the RAG TF-IDF index if documents have changed.

    Returns a dict with keys:
        ``rebuilt``  — True if the index was rebuilt, False if it was up-to-date.
        ``chunks``   — Number of chunks in the (re)built index.
        ``skipped``  — True when RAG_ENABLED=false.
        ``error``    — Set when an exception occurred (index rebuild failed).
    """
    try:
        from app.core.config import settings  # noqa: PLC0415

        if not settings.rag_enabled:
            logger.debug("rag.rebuild_index: RAG_ENABLED=false, skipping")
            return {"rebuilt": False, "chunks": 0, "skipped": True}

        from app.services.rag.retrieval_service import (  # noqa: PLC0415
            _build_tfidf_index,
            _docs_hash,
            _load_docs,
            _load_persisted_index,
            _persist_index,
            set_index,
        )

        raw_docs = _load_docs(settings.rag_docs_root)
        current_hash = _docs_hash(raw_docs)

        # Check if the persisted index is already up-to-date.
        persisted = _load_persisted_index(settings.rag_vector_store_path)
        if persisted and persisted.doc_hash == current_hash:
            logger.debug(
                "rag.rebuild_index: index is up-to-date (hash=%s), skipping rebuild",
                current_hash[:12],
            )
            return {"rebuilt": False, "chunks": len(persisted.chunks), "skipped": False}

        # Docs changed (or no persisted index) — rebuild.
        logger.info(
            "rag.rebuild_index: docs changed (hash=%s → %s), rebuilding index",
            (persisted.doc_hash[:12] if persisted else "none"),
            current_hash[:12],
        )
        idx = _build_tfidf_index(settings.rag_docs_root, settings.rag_chunk_size, settings.rag_chunk_overlap)
        _persist_index(idx, settings.rag_vector_store_path)

        # Invalidate the in-process cached index so workers pick up the new one.
        set_index(idx)

        logger.info("rag.rebuild_index: rebuilt with %d chunks", len(idx.chunks))
        return {"rebuilt": True, "chunks": len(idx.chunks), "skipped": False}

    except Exception as exc:  # noqa: BLE001
        logger.error("rag.rebuild_index failed: %s", exc)
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {"rebuilt": False, "chunks": 0, "skipped": False, "error": str(exc)}
