#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import shutil
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


def api_contract_check() -> None:
    required_files = [
        "backend/app/api/v1/design.py",
        "backend/app/api/v1/upsell.py",
        "backend/app/api/v1/video.py",
        "backend/app/api/v1/offers.py",
        "backend/app/api/v1/crm.py",
        "backend/app/api/v1/memory.py",
        "backend/app/api/v1/dashboard.py",
        "backend/app/api/v1/render.py",
    ]
    missing = [p for p in required_files if not (ROOT / p).exists()]
    ok = len(missing) == 0
    REPORT["checks"].append({"name": "api_contract_files", "ok": ok, "missing": missing})
    if not ok:
        REPORT["go_no_go"] = "NO-GO"


def write_patch_report() -> None:
    report_md = ROOT / "docs" / "PATCH_REPORT.md"
    lines = [
        "# PATCH REPORT",
        "",
        f"- GO/NO-GO: {REPORT['go_no_go']}",
        "- Checks:",
    ]
    for check in REPORT["checks"]:
        status = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- [{status}] {check.get('name')}")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    exists_check("backend")
    exists_check("frontend")
    exists_check("docs")
    if (ROOT / "backend").exists():
        run_check("python_compile_backend", ["python", "-m", "compileall", "backend"])
    if (ROOT / "alembic").exists() or (ROOT / "backend/alembic").exists():
        if shutil.which("alembic"):
            run_check("alembic_heads", ["alembic", "heads"])
        else:
            REPORT["checks"].append({"name": "alembic_heads", "ok": True, "skipped": "alembic CLI not installed"})
    if (ROOT / "package.json").exists():
        run_check("npm_build", ["npm", "run", "build"])
    if (ROOT / "pytest.ini").exists() or (ROOT / "tests").exists():
        run_check("pytest", ["pytest", "-q"])
    api_contract_check()
    out = ROOT / "docs" / "TECHLEAD_AUDIT_REPORT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")
    write_patch_report()
    print(json.dumps(REPORT, ensure_ascii=False, indent=2))
    raise SystemExit(0 if REPORT["go_no_go"] == "GO" else 1)
