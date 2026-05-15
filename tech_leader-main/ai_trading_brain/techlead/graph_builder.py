from __future__ import annotations

import ast
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .file_inventory import FileInventory, FileRecord

class ContextGraphBuilder:
    """Builds a real static Context Graph from repository files."""

    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.inventory = FileInventory(self.repo_root)

    def build(self) -> dict[str, Any]:
        files = self.inventory.code_files()
        entities: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        module_by_path: dict[str, str] = {}
        for f in files:
            if f.suffix == ".py":
                module_by_path[f.rel] = f.rel[:-3].replace("/", ".")
            entities.append(self._file_entity(f))

        for f in files:
            if f.suffix == ".py":
                text = self.inventory.read_text(f)
                try:
                    tree = ast.parse(text, filename=f.rel)
                except SyntaxError:
                    continue
                module = module_by_path.get(f.rel, f.rel)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        entity_id = f"function:{module}.{node.name}"
                        entities.append({"id": entity_id, "type": "function", "name": node.name, "path": f.rel, "lineno": node.lineno})
                        edges.append({"source": f"file:{f.rel}", "target": entity_id, "type": "defines"})
                    elif isinstance(node, ast.ClassDef):
                        entity_id = f"class:{module}.{node.name}"
                        entities.append({"id": entity_id, "type": "class", "name": node.name, "path": f.rel, "lineno": node.lineno})
                        edges.append({"source": f"file:{f.rel}", "target": entity_id, "type": "defines"})
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            edges.append({"source": f"file:{f.rel}", "target": f"module:{alias.name}", "type": "imports"})
                    elif isinstance(node, ast.ImportFrom):
                        target = self._resolve_import_from(module, node)
                        edges.append({"source": f"file:{f.rel}", "target": f"module:{target}", "type": "imports"})

        risk = self._risk_signals(files, edges)
        return {"entities": entities, "edges": edges, "risk_signals": risk, "summary": {"files": len(files), "entities": len(entities), "edges": len(edges)}}

    def _file_entity(self, f: FileRecord) -> dict[str, Any]:
        h = hashlib.sha256()
        try:
            h.update(f.path.read_bytes()[:2_000_000])
        except Exception:
            pass
        return {"id": f"file:{f.rel}", "type": "file", "path": f.rel, "suffix": f.suffix, "size": f.size, "sha256": h.hexdigest()}

    def _resolve_import_from(self, module: str, node: ast.ImportFrom) -> str:
        base = node.module or ""
        if node.level <= 0:
            return base
        parts = module.split(".")[:-node.level]
        if base:
            parts.append(base)
        return ".".join(parts)

    def _risk_signals(self, files: list[FileRecord], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        by_name = {f.rel for f in files}
        required = [
            ("agent runtime", ["ai_trading_brain/brain_runtime.py", "ai_trading_brain/unified_trade_pipeline.py"]),
            ("governance", ["ai_trading_brain/governance.py"]),
            ("memory", ["ai_trading_brain/memory_engine.py"]),
            ("backend api", ["backend/main.py"]),
        ]
        for label, options in required:
            if not any(o in by_name for o in options):
                signals.append({"severity": "P1", "type": "missing_layer", "layer": label, "expected_any": options})
        import_counts: dict[str, int] = defaultdict(int)
        for e in edges:
            if e.get("type") == "imports":
                import_counts[e["target"]] += 1
        for mod, count in import_counts.items():
            if count >= 15 and not (mod.startswith("typing") or mod in {"os", "sys", "json", "pathlib"}):
                signals.append({"severity": "P2", "type": "high_coupling_import", "module": mod, "count": count})
        return signals

    def write(self, out_dir: str | Path) -> dict[str, Any]:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        graph = self.build()
        (out / "entities.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in graph["entities"]) + "\n", encoding="utf-8")
        (out / "edges.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in graph["edges"]) + "\n", encoding="utf-8")
        (out / "graph_summary.json").write_text(json.dumps(graph["summary"], ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "risk_signals.json").write_text(json.dumps(graph["risk_signals"], ensure_ascii=False, indent=2), encoding="utf-8")
        return graph
