import json
from pathlib import Path
from typing import Dict, Any

class BrandMemoryCloud:
    def __init__(self, path="storage/brand_memory.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, record: Dict[str, Any]):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"saved": True, "path": str(self.path), "record_id": record.get("run_id")}

    def recall(self, brand_name: str, limit=10):
        if not self.path.exists():
            return []
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if item.get("brand_name", "").lower() == brand_name.lower():
                rows.append(item)
        return rows[-limit:]
