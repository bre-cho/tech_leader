from __future__ import annotations

from typing import Any
from app.memory.local_second_brain import LocalSecondBrainStore
from app.memory.topology import ALL_LAYERS


class MemoryAuditor:
    def __init__(self, store: LocalSecondBrainStore | None = None):
        self._store = store or LocalSecondBrainStore()

    def run(self) -> dict[str, Any]:
        records = self._store.all()

        layers_detected = list({r.layer for r in records})
        missing_layers = [l for l in ALL_LAYERS if l not in layers_detected]

        from datetime import datetime, timezone

        def is_stale(r) -> bool:
            meta = r.metadata or {}
            expires_at = meta.get("expires_at")
            if not expires_at:
                return False
            try:
                exp = datetime.fromisoformat(expires_at)
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                return datetime.now(timezone.utc) > exp
            except Exception:
                return False

        stale = [{"id": r.id, "title": r.title, "layer": r.layer} for r in records if is_stale(r)]

        # Conflicting: same title, same namespace but different content
        seen: dict[str, list] = {}
        for r in records:
            key = f"{r.namespace}:{r.title}"
            seen.setdefault(key, []).append(r)
        conflicting = [
            {"key": k, "count": len(v), "ids": [x.id for x in v]}
            for k, v in seen.items()
            if len(v) > 1
        ]

        # Unlinked: no source_agent_id
        unlinked = [r.id for r in records if not getattr(r, "source_agent_id", None) or r.source_agent_id == "unknown"]

        status = "PASS" if not missing_layers and not stale and not conflicting else "WARN"

        repair = []
        if missing_layers:
            repair.append(f"Write at least one record per missing layer: {missing_layers}")
        if stale:
            repair.append(f"Evict or refresh {len(stale)} stale memory record(s)")
        if conflicting:
            repair.append(f"Resolve {len(conflicting)} conflicting memory title(s)")

        return {
            "memory_topology_status": status,
            "total_records": len(records),
            "memory_layers_detected": layers_detected,
            "missing_memory_layers": missing_layers,
            "stale_memory": stale[:20],
            "conflicting_memory": conflicting[:20],
            "unlinked_memory_records": unlinked[:20],
            "repair_plan": repair,
        }
