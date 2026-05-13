from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


class MemoryStore:
    def __init__(self, path: str = "storage/memory/winner_dna.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, record: Dict[str, Any]):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"saved": True, "path": str(self.path), "record_id": record.get("run_id")}

    def recent(self, limit: int = 20):
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in lines if line.strip()]
