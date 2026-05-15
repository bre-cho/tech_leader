from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MEMORY_PATH = Path("docs/runtime/engineering-memory.jsonl")


def append_memory_event(repo_root: str | Path, event: dict[str, Any]) -> Path:
    root = Path(repo_root)
    path = root / MEMORY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    enriched = {"created_at": datetime.now(timezone.utc).isoformat(), **event}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(enriched, ensure_ascii=False) + "\n")
    return path


def load_memory_events(repo_root: str | Path, limit: int = 100) -> list[dict[str, Any]]:
    path = Path(repo_root) / MEMORY_PATH
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows
