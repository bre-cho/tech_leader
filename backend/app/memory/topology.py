from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


class MemoryLayer(str, Enum):
    short_term = "short_term"
    long_term = "long_term"
    task = "task"
    skill = "skill"
    failure = "failure"
    decision = "decision"
    artifact = "artifact"
    organization = "organization"
    economic = "economic"


ALL_LAYERS = [layer.value for layer in MemoryLayer]


@dataclass
class LayeredMemoryRecord:
    """A memory record enriched with topology metadata."""

    id: str
    kind: str
    namespace: str
    title: str
    content: str
    layer: MemoryLayer
    version: int = 1
    source_agent_id: str = "unknown"
    lineage_id: Optional[str] = None
    expires_at: Optional[str] = None
    tags: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_stale(self) -> bool:
        if not self.expires_at:
            return False
        try:
            exp = datetime.fromisoformat(self.expires_at)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) > exp
        except ValueError:
            return False
