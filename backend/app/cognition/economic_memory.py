from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


_DEFAULT_PATH = "storage/economic_memory.jsonl"


class EconomicMemoryStore:
    """
    Lightweight JSONL store for growth loop patterns and revenue intelligence.
    Production mapping: JSONL → Cloudflare D1 or dedicated KV store.
    """

    def __init__(self, path: str = _DEFAULT_PATH):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def store(self, record: dict[str, Any]) -> dict[str, Any]:
        record = {
            **record,
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def all(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        results = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return results

    def get_growth_loops(self) -> list[dict[str, Any]]:
        return [r for r in self.all() if r.get("record_type") == "growth_loop"]

    def get_revenue_intelligence(self) -> list[dict[str, Any]]:
        return [r for r in self.all() if r.get("record_type") == "revenue_intelligence"]
