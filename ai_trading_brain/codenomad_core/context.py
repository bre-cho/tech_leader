from __future__ import annotations

import json
from pathlib import Path
from .models import ProjectContext, ProjectFile, utc_now

IGNORED_DIRS = {".git", ".pytest_cache", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", ".next", "coverage"}
SOURCE_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".md", ".json", ".yml", ".yaml", ".toml"}
PACKAGE_MARKERS = {"package.json", "pyproject.toml", "requirements.txt", "poetry.lock", "pnpm-lock.yaml", "package-lock.json", "uv.lock"}


def _kind(path: Path) -> str:
    name = path.name.lower()
    if name in PACKAGE_MARKERS:
        return "package-manager"
    if "test" in name or path.parent.name == "tests":
        return "test"
    if path.suffix in {".md", ".rst"}:
        return "docs"
    if path.suffix in {".py", ".ts", ".tsx", ".js", ".jsx"}:
        return "source"
    if path.suffix in {".json", ".yml", ".yaml", ".toml"}:
        return "config"
    return "other"


def _risk_flags(rel: str, text: str) -> list[str]:
    flags: list[str] = []
    lower = text.lower()
    if any(token in lower for token in ["rm -rf", "drop table", "delete from", "truncate table"]):
        flags.append("destructive-command-or-sql")
    if any(token in lower for token in ["api_key", "secret", "password", "private_key"]):
        flags.append("possible-secret-reference")
    if rel.endswith(("settings.py", ".env", ".env.example")):
        flags.append("sensitive-config")
    return flags


def scan_project_context(repo_root: str | Path, max_files: int = 500) -> ProjectContext:
    root = Path(repo_root).resolve()
    files: list[ProjectFile] = []
    languages: dict[str, int] = {}
    docs_present: list[str] = []
    tests_present: list[str] = []
    scripts_present: list[str] = []
    package_managers: list[str] = []
    risk_summary: list[str] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix not in SOURCE_EXT and path.name not in PACKAGE_MARKERS:
            continue
        rel = str(path.relative_to(root))
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        lines = 0 if not text else text.count("\n") + 1
        flags = _risk_flags(rel, text[:200_000])
        kind = _kind(path)
        files.append(ProjectFile(rel, kind, path.stat().st_size, lines, flags))
        languages[path.suffix or path.name] = languages.get(path.suffix or path.name, 0) + 1
        if kind == "docs":
            docs_present.append(rel)
        elif kind == "test":
            tests_present.append(rel)
        elif rel.startswith("scripts/"):
            scripts_present.append(rel)
        elif kind == "package-manager":
            package_managers.append(rel)
        for f in flags:
            risk_summary.append(f"{rel}: {f}")
        if len(files) >= max_files:
            risk_summary.append(f"scan-truncated-after-{max_files}-files")
            break

    return ProjectContext(
        repo_root=str(root),
        generated_at=utc_now(),
        files=files,
        languages=dict(sorted(languages.items())),
        docs_present=docs_present[:80],
        tests_present=tests_present[:80],
        scripts_present=scripts_present[:80],
        package_managers=package_managers,
        risk_summary=risk_summary[:100],
    )


def write_context(context: ProjectContext, out: str | Path) -> Path:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(context.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
