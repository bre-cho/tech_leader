#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path.cwd()
REPORT = {"checks": [], "go_no_go": "GO"}


def run_check(name: str, cmd: list[str]) -> None:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=120)
        ok = proc.returncode == 0
        REPORT["checks"].append({"name": name, "ok": ok, "stdout": proc.stdout[-3000:], "stderr": proc.stderr[-3000:]})
        if not ok:
            REPORT["go_no_go"] = "NO-GO"
    except Exception as exc:
        REPORT["checks"].append({"name": name, "ok": False, "error": str(exc)})
        REPORT["go_no_go"] = "NO-GO"


def exists_check(path: str) -> None:
    ok = (ROOT / path).exists()
    REPORT["checks"].append({"name": f"exists:{path}", "ok": ok})
    if not ok:
        REPORT["go_no_go"] = "NO-GO"


if __name__ == "__main__":
    exists_check("backend")
    exists_check("frontend")
    exists_check("docs")
    if (ROOT / "backend").exists():
        run_check("python_compile_backend", ["python", "-m", "compileall", "backend"])
    if (ROOT / "package.json").exists():
        run_check("npm_build", ["npm", "run", "build"])
    if (ROOT / "pytest.ini").exists() or (ROOT / "tests").exists():
        run_check("pytest", ["pytest", "-q"])
    out = ROOT / "docs" / "TECHLEAD_AUDIT_REPORT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(REPORT, ensure_ascii=False, indent=2))
    raise SystemExit(0 if REPORT["go_no_go"] == "GO" else 1)
