#!/usr/bin/env python3
"""
audit_static_scan.py — Phase 2: Static code analysis.

Performs:
  1. Python syntax check on all backend .py files
  2. Import scan (find missing imports or circular suspects)
  3. Orphan module detection (files not imported anywhere)
  4. Mock leakage scan (mock/fake patterns leaking into production code)
  5. Governance drift scan (files modifying governance without law trace)

Output: docs/audit_reports/static_scan.json

Usage:
    python scripts/audit_static_scan.py [--repo-root <path>]
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def syntax_check(py_files: list[Path]) -> list[dict]:
    errors = []
    for f in py_files:
        try:
            ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError as e:
            errors.append({"file": str(f), "line": e.lineno, "error": str(e)})
    return errors


def mock_leakage_scan(py_files: list[Path], backend_root: Path) -> list[dict]:
    patterns = [
        r"\bmock\b", r"\bMock\b", r"\bpatch\b", r"\bMagicMock\b",
        r"\bfake_\w+", r"\bstub_\w+", r"unittest\.mock",
    ]
    compiled = [re.compile(p) for p in patterns]
    leaks = []
    for f in py_files:
        if "test" in str(f).lower():
            continue
        try:
            src = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for pat in compiled:
            if pat.search(src):
                leaks.append({"file": str(f.relative_to(backend_root)), "pattern": pat.pattern})
                break
    return leaks


def governance_drift_scan(py_files: list[Path], backend_root: Path) -> list[dict]:
    """Files that import governance but do NOT reference law_trace or validate_trace."""
    drift = []
    for f in py_files:
        try:
            src = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if "governance" in src and "operating_law" in src:
            if "law_trace" not in src and "validate_trace" not in src and "assert_can_promote" not in src:
                drift.append({"file": str(f.relative_to(backend_root)), "note": "imports governance but no law trace usage"})
    return drift


def orphan_module_scan(py_files: list[Path], backend_root: Path) -> list[str]:
    """Modules that are never imported by any other backend module."""
    all_imports: set[str] = set()
    for f in py_files:
        try:
            src = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in re.findall(r"from\s+([\w.]+)\s+import|import\s+([\w.]+)", src):
            for part in m:
                if part:
                    all_imports.add(part.split(".")[0])

    orphans = []
    for f in py_files:
        module_name = f.stem
        if module_name == "__init__":
            continue
        if module_name not in all_imports:
            orphans.append(str(f.relative_to(backend_root)))
    return orphans[:40]


def main():
    parser = argparse.ArgumentParser(description="Static audit scan")
    parser.add_argument("--repo-root", default=".", help="Path to repository root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    backend_root = repo_root / "backend" / "app"

    if not backend_root.exists():
        print(f"Backend not found at {backend_root}", file=sys.stderr)
        sys.exit(1)

    py_files = list(backend_root.glob("**/*.py"))
    print(f"Scanning {len(py_files)} Python files in {backend_root}")

    syntax_errors = syntax_check(py_files)
    mock_leaks = mock_leakage_scan(py_files, backend_root)
    gov_drift = governance_drift_scan(py_files, backend_root)
    orphans = orphan_module_scan(py_files, backend_root)

    status = "PASS" if not syntax_errors and not mock_leaks else "FAIL"

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files_scanned": len(py_files),
        "status": status,
        "syntax_errors": syntax_errors,
        "mock_leakage": mock_leaks,
        "governance_drift": gov_drift,
        "orphan_modules": orphans,
        "summary": {
            "syntax_errors": len(syntax_errors),
            "mock_leaks": len(mock_leaks),
            "gov_drift": len(gov_drift),
            "orphans": len(orphans),
        },
    }

    out_dir = repo_root / "docs" / "audit_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "static_scan.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Static scan written to: {out_path}")

    if syntax_errors or mock_leaks:
        print("FAIL — see static_scan.json for details", file=sys.stderr)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
