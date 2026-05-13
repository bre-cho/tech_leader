from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class JSONLStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, item: BaseModel):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(item.model_dump_json() + "\n")

    def all(self, cls: Type[T]) -> list[T]:
        if not self.path.exists():
            return []
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(cls.model_validate_json(line))
        return rows

    def overwrite(self, items: Iterable[BaseModel]):
        self.path.write_text("\n".join([i.model_dump_json() for i in items]) + "\n", encoding="utf-8")
