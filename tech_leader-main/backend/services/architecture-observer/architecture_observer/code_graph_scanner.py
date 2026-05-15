from __future__ import annotations
import ast, datetime as dt, hashlib, json, re
from pathlib import Path
from .models import CodeEdge, CodeGraphSnapshot, CodeNode

SUPPORTED_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml", ".md", ".toml"}
SKIP_DIRS = {".git", "node_modules", ".next", "__pycache__", ".venv", "dist", "build", ".agent16"}

def stable_id(path: str) -> str:
    return hashlib.sha1(path.encode("utf-8")).hexdigest()[:16]

def infer_kind(path: Path) -> str:
    if path.suffix == ".py": return "python"
    if path.suffix in {".ts", ".tsx"}: return "typescript"
    if path.suffix in {".js", ".jsx"}: return "javascript"
    if path.suffix in {".json", ".yaml", ".yml", ".toml"}: return "config"
    if path.suffix == ".md": return "doc"
    return "unknown"

def infer_layer(rel: str) -> str:
    first = rel.split("/", 1)[0]
    if first in {"apps", "app", "components", "pages"}: return "frontend"
    if first == "services": return "service"
    if first == "agents": return "agent"
    if first == "workflows": return "workflow"
    if first == "runtime": return "runtime"
    if first == "memory": return "memory"
    if first == "context-graph": return "context_graph"
    if first in {"tests", "__tests__"} or rel.endswith(".test.ts") or rel.endswith("_test.py"): return "test"
    if first == "docs": return "docs"
    if first == "lib": return "library"
    return first or "root"

def infer_module(rel: str) -> str:
    parts = rel.split("/")
    return "/".join(parts[:2]) if len(parts) >= 2 else parts[0]

def scan_python(text: str):
    imports, functions, classes = [], [], []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return imports, functions, classes
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
    return imports, functions, classes

def scan_ts_js(text: str):
    imports, exports, functions = [], [], []
    imports.extend(re.findall(r"from\s+['\"]([^'\"]+)['\"]", text))
    imports.extend(re.findall(r"import\(['\"]([^'\"]+)['\"]\)", text))
    exports.extend(re.findall(r"export\s+(?:default\s+)?(?:function|class|const|let|var|type|interface)\s+([A-Za-z0-9_]+)", text))
    functions.extend(re.findall(r"function\s+([A-Za-z0-9_]+)\s*\(", text))
    functions.extend(re.findall(r"const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\(", text))
    return imports, exports, functions

def risk_tags(text: str, rel: str):
    tags, lower = [], text.lower()
    if "subprocess" in lower or "shell=true" in lower or "child_process" in lower: tags.append("shell_execution")
    if "eval(" in lower or "exec(" in lower: tags.append("dynamic_execution")
    if "api_key" in lower or "secret" in lower or "password" in lower: tags.append("credential_touch")
    if "alembic" in lower or "migration" in lower: tags.append("database_migration")
    if "/api/" in rel or "route.ts" in rel: tags.append("api_surface")
    if "provider" in lower: tags.append("provider_runtime")
    return sorted(set(tags))

def iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in SUPPORTED_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p

def resolve_import(source_path: str, imp: str, id_by_path: dict[str, str]):
    if imp.startswith("@/"):
        candidate = imp[2:]
    elif imp.startswith("./") or imp.startswith("../"):
        candidate = (Path(source_path).parent / imp).as_posix()
    else:
        return None
    for c in [candidate, candidate+".ts", candidate+".tsx", candidate+".js", candidate+".jsx", candidate+".py", candidate+"/index.ts", candidate+"/index.tsx"]:
        normalized = str(Path(c)).replace("\\", "/")
        if normalized in id_by_path:
            return id_by_path[normalized]
    return None

def count_by(items):
    out = {}
    for item in items:
        out[str(item)] = out.get(str(item), 0) + 1
    return out

def scan_repo(root: Path) -> CodeGraphSnapshot:
    root = root.resolve()
    nodes, edges, modules = [], [], {}
    for p in iter_files(root):
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="ignore")
        kind = infer_kind(p)
        imports, exports, functions, classes = [], [], [], []
        if kind == "python":
            imports, functions, classes = scan_python(text)
        elif kind in {"typescript", "javascript"}:
            imports, exports, functions = scan_ts_js(text)
        node = CodeNode(id=stable_id(rel), path=rel, module=infer_module(rel), kind=kind, layer=infer_layer(rel), size_bytes=p.stat().st_size, lines=text.count("\n")+1, imports=imports, exports=exports, functions=functions, classes=classes, risk_tags=risk_tags(text, rel))
        nodes.append(node)
        modules.setdefault(node.module, []).append(node.path)
    id_by_path = {n.path: n.id for n in nodes}
    for node in nodes:
        for imp in node.imports:
            target = resolve_import(node.path, imp, id_by_path)
            if target:
                edges.append(CodeEdge(source=node.id, target=target, relation="imports", evidence=imp))
    summary = {"node_count": len(nodes), "edge_count": len(edges), "module_count": len(modules), "layers": count_by([n.layer for n in nodes]), "kinds": count_by([n.kind for n in nodes]), "risk_tags": count_by(tag for n in nodes for tag in n.risk_tags)}
    return CodeGraphSnapshot(snapshot_id=hashlib.sha1(json.dumps(summary, sort_keys=True).encode()).hexdigest()[:16], repo_root=str(root), created_at=dt.datetime.utcnow().isoformat()+"Z", nodes=nodes, edges=edges, modules=modules, summary=summary)
