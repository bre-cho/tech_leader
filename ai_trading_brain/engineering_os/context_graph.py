from __future__ import annotations

import ast
import re
from pathlib import Path
from .models import ContextGraph, EngineeringEdge, EngineeringNode, NodeKind

IGNORE_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "dist", "build", ".venv", "venv"}
LANG_BY_SUFFIX = {
    ".py": "python", ".ts": "typescript", ".tsx": "typescript-react", ".js": "javascript", ".jsx": "javascript-react",
    ".md": "markdown", ".json": "json", ".yml": "yaml", ".yaml": "yaml", ".toml": "toml", ".sql": "sql",
}


def _kind(path: Path) -> NodeKind:
    p = str(path).replace("\\", "/")
    name = path.name.lower()
    if "/tests/" in f"/{p}" or name.startswith("test_") or name.endswith(".test.ts") or name.endswith(".spec.ts"):
        return "test"
    if "/scripts/" in f"/{p}" or path.parent.name == "scripts":
        return "script"
    if "/docs/" in f"/{p}" or path.suffix.lower() == ".md":
        return "doc"
    if "/skills/" in f"/{p}":
        return "skill"
    if name in {"package.json", "pyproject.toml", "pytest.ini", "tsconfig.json"} or "/.github/workflows/" in f"/{p}":
        return "config" if "/.github/workflows/" not in f"/{p}" else "workflow"
    if path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx"}:
        return "module"
    return "unknown"


def _python_imports_exports(path: Path) -> tuple[list[str], list[str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return [], []
    imports: list[str] = []
    exports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                exports.append(node.name)
    return sorted(set(imports)), sorted(set(exports))


def _text_imports(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:20000]
    except Exception:
        return []
    patterns = [r"from ['\"]([^'\"]+)", r"import .* from ['\"]([^'\"]+)", r"require\(['\"]([^'\"]+)"]
    found: list[str] = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text))
    return sorted(set(x.split("/")[0] for x in found))


def build_context_graph(repo_root: str | Path) -> ContextGraph:
    root = Path(repo_root).resolve()
    nodes: list[EngineeringNode] = []
    by_path: dict[str, EngineeringNode] = {}
    for path in root.rglob("*"):
        if path.is_dir() or any(part in IGNORE_DIRS for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        if suffix not in LANG_BY_SUFFIX and path.name not in {"AGENTS.md", "Dockerfile"}:
            continue
        imports, exports = ([], [])
        if suffix == ".py":
            imports, exports = _python_imports_exports(path)
        elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
            imports = _text_imports(path)
        tags = []
        if "migration" in rel.lower(): tags.append("migration")
        if "route" in rel.lower() or "api" in rel.lower(): tags.append("api")
        if "worker" in rel.lower(): tags.append("worker")
        if "test" in rel.lower(): tags.append("verification")
        node = EngineeringNode(
            id=rel,
            path=rel,
            kind=_kind(path),
            language=LANG_BY_SUFFIX.get(suffix, "text"),
            size_bytes=path.stat().st_size,
            imports=imports,
            exports=exports,
            tags=tags,
        )
        nodes.append(node)
        by_path[rel] = node
    edges: list[EngineeringEdge] = []
    module_names = {Path(n.path).stem: n.path for n in nodes if n.language == "python"}
    for node in nodes:
        for imp in node.imports:
            if imp in module_names:
                edges.append(EngineeringEdge(source=node.path, target=module_names[imp], relation="imports", weight=1.0))
        if node.kind == "test":
            for n in nodes:
                if n.kind == "module" and Path(n.path).stem in " ".join(node.imports + node.exports + [node.path]):
                    edges.append(EngineeringEdge(source=node.path, target=n.path, relation="verifies", weight=0.7))
    stats = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "by_kind": {kind: sum(1 for n in nodes if n.kind == kind) for kind in sorted({n.kind for n in nodes})},
        "high_risk_files": [n.path for n in nodes if any(t in n.tags for t in ["migration", "api", "worker"])],
    }
    return ContextGraph(repo_root=str(root), nodes=nodes, edges=edges, stats=stats)
