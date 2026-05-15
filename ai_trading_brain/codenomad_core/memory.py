from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from .models import utc_now


def append_session_memory(repo_root: str | Path, event: dict[str, Any]) -> Path:
    root = Path(repo_root).resolve()
    path = root / ".codenomad_core" / "sessions.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"created_at": utc_now(), **event}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return path
