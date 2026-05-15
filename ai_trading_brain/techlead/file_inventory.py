from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

IGNORE_DIRS = {'.git', '.venv', 'venv', 'node_modules', '.next', 'dist', 'build', '__pycache__', '.pytest_cache', '.mypy_cache'}
CODE_EXTS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.yaml', '.yml', '.toml', '.md'}

@dataclass(frozen=True)
class FileRecord:
    path: Path
    rel: str
    suffix: str
    size: int

class FileInventory:
    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()

    def iter_files(self) -> list[FileRecord]:
        records: list[FileRecord] = []
        for root, dirs, names in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for name in names:
                p = Path(root) / name
                try:
                    rel = str(p.relative_to(self.repo_root)).replace(os.sep, '/')
                    st = p.stat()
                except OSError:
                    continue
                records.append(FileRecord(path=p, rel=rel, suffix=p.suffix.lower(), size=st.st_size))
        return records

    def code_files(self) -> list[FileRecord]:
        return [f for f in self.iter_files() if f.suffix in CODE_EXTS and f.size < 2_000_000]

    def exists_any(self, candidates: list[str]) -> bool:
        return any((self.repo_root / c).exists() for c in candidates)

    def read_text(self, record: FileRecord) -> str:
        try:
            return record.path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ''
