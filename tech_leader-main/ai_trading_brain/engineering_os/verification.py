from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from .models import VerificationCheck, VerificationReport


def _run(cmd: list[str], cwd: Path, timeout: int = 60) -> VerificationCheck:
    name = " ".join(cmd)
    try:
        result = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
        output = (result.stdout or "") + (result.stderr or "")
        return VerificationCheck(name=name, command=name, passed=result.returncode == 0, output=output.strip() or "<no output>")
    except Exception as exc:
        return VerificationCheck(name=name, command=name, passed=False, output=f"{type(exc).__name__}: {exc}")


def run_verification(task: str, repo_root: str | Path = ".", include_pytest: bool = True) -> VerificationReport:
    root = Path(repo_root).resolve()
    py_files = [str(p.relative_to(root)) for p in root.rglob("*.py") if "__pycache__" not in p.parts and ".venv" not in p.parts]
    checks: list[VerificationCheck] = []
    if py_files:
        checks.append(_run([sys.executable, "-m", "py_compile", *py_files[:200]], root, timeout=120))
    if include_pytest and (root / "tests").exists():
        checks.append(_run([sys.executable, "-m", "pytest", "-q"], root, timeout=120))
    if (root / "AGENTS.md").exists():
        checks.append(VerificationCheck(name="constitution", command="test -f AGENTS.md", passed=True, output="AGENTS.md present"))
    else:
        checks.append(VerificationCheck(name="constitution", command="test -f AGENTS.md", passed=False, output="AGENTS.md missing"))
    passed = all(check.passed for check in checks)
    recommendations = [] if passed else ["Fix failed checks before release", "Update docs/runtime/verification-report.md after rerun"]
    return VerificationReport(task=task, passed=passed, checks=checks, recommendations=recommendations)
