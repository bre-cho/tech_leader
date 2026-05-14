from __future__ import annotations

from typing import Any, Optional
from app.memory.topology import MemoryLayer, LayeredMemoryRecord, ALL_LAYERS


class MemoryManager:
    """
    Unified interface for read/write operations across all memory layers.

    In production this wraps the actual persistence backend (LocalSecondBrainStore
    or CloudflareSecondBrainAdapter). For audit purposes it can also operate on
    an in-memory list injected at construction time.
    """

    def __init__(self, store=None):
        # store: any object that exposes .all() -> list[MemoryRecord] and .create(...)
        self._store = store
        self._in_memory: list[LayeredMemoryRecord] = []

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def write(
        self,
        record: LayeredMemoryRecord,
        *,
        conflict_strategy: str = "overwrite",
    ) -> LayeredMemoryRecord:
        """Write a record to the appropriate memory layer."""
        existing = self._find(record.id)
        if existing:
            if conflict_strategy == "reject":
                raise ValueError(
                    f"Memory conflict: record '{record.id}' already exists in layer "
                    f"'{existing.layer}' — attempted write to layer '{record.layer}'"
                )
            # overwrite — bump version
            record.version = existing.version + 1
            self._in_memory = [r for r in self._in_memory if r.id != record.id]

        self._in_memory.append(record)

        if self._store is not None:
            from app.memory.contracts import MemoryCreateRequest

            req = MemoryCreateRequest(
                kind=record.kind,
                namespace=record.namespace,
                title=record.title,
                content=record.content,
                tags=record.tags,
                metadata={
                    **record.metadata,
                    "layer": record.layer.value,
                    "version": record.version,
                    "source_agent_id": record.source_agent_id,
                    "lineage_id": record.lineage_id,
                    "expires_at": record.expires_at,
                },
            )
            self._store.create(req)

        return record

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def read_by_layer(
        self,
        layer: MemoryLayer,
        *,
        include_stale: bool = False,
    ) -> list[LayeredMemoryRecord]:
        results = [r for r in self._in_memory if r.layer == layer]
        if not include_stale:
            results = [r for r in results if not r.is_stale()]
        return results

    def read_all(self, *, include_stale: bool = False) -> list[LayeredMemoryRecord]:
        if not include_stale:
            return [r for r in self._in_memory if not r.is_stale()]
        return list(self._in_memory)

    # ------------------------------------------------------------------
    # Audit helpers
    # ------------------------------------------------------------------
    def detect_stale(self) -> list[LayeredMemoryRecord]:
        return [r for r in self._in_memory if r.is_stale()]

    def detect_missing_layers(self) -> list[str]:
        present = {r.layer.value for r in self._in_memory}
        return [l for l in ALL_LAYERS if l not in present]

    def detect_version_conflicts(self) -> list[dict[str, Any]]:
        """Find records with the same id but different version — indicates write collision."""
        seen: dict[str, list[LayeredMemoryRecord]] = {}
        for r in self._in_memory:
            seen.setdefault(r.id, []).append(r)
        return [
            {"id": rid, "versions": [r.version for r in recs]}
            for rid, recs in seen.items()
            if len(recs) > 1
        ]

    def detect_missing_source_agent(self) -> list[str]:
        return [r.id for r in self._in_memory if not r.source_agent_id or r.source_agent_id == "unknown"]

    # ------------------------------------------------------------------
    def _find(self, record_id: str) -> Optional[LayeredMemoryRecord]:
        for r in self._in_memory:
            if r.id == record_id:
                return r
        return None
