from __future__ import annotations
import ast
from pathlib import Path
from .models import FileNode, DependencyEvolutionSnapshot

class DependencyEvolutionGraph:
    """Builds a lightweight Python import graph and identifies dependency hotspots."""

    def __init__(self, repo_root: str | Path):
        self.repo_root = Path(repo_root)

    def build(self, previous_files: set[str] | None = None) -> DependencyEvolutionSnapshot:
        nodes: list[FileNode] = []
        edges: list[dict] = []
        for file in self.repo_root.rglob("*.py"):
            if any(part.startswith(".") or part == "__pycache__" for part in file.parts):
                continue
            rel = file.relative_to(self.repo_root).as_posix()
            imports = self._imports(file)
            nodes.append(FileNode(path=rel, imports=imports, size_bytes=file.stat().st_size))
            for imp in imports:
                edges.append({"source": rel, "target": imp, "relation": "imports", "weight": 1.0})
        inbound: dict[str, int] = {}
        for edge in edges:
            inbound[edge["target"]] = inbound.get(edge["target"], 0) + 1
        hotspots = [k for k, v in sorted(inbound.items(), key=lambda x: x[1], reverse=True)[:20] if v >= 2]
        current = {n.path for n in nodes}
        changed = sorted(current - (previous_files or set()))
        return DependencyEvolutionSnapshot(nodes=nodes, edges=edges, changed_since_last=changed, hotspots=hotspots)

    def _imports(self, file: Path) -> list[str]:
        try:
            tree = ast.parse(file.read_text(encoding="utf-8"))
        except Exception:
            return []
        out: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                out.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                out.append(node.module)
        return sorted(set(out))
