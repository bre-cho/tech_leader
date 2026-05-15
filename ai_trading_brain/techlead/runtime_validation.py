from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .models import Finding

class RuntimeValidator:
    def __init__(self, repo_root: str | Path, timeout_seconds: int = 45) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.timeout_seconds = timeout_seconds

    def validate(self) -> tuple[dict[str, Any], list[Finding]]:
        checks = self._detect_commands()
        results: dict[str, Any] = {}
        findings: list[Finding] = []
        for name, cmd in checks.items():
            res = self._run(cmd)
            results[name] = res
            if res['returncode'] != 0:
                severity = 'P1' if name in {'python_compile', 'pytest'} else 'P2'
                findings.append(Finding(severity,'PHASE_3_RUNTIME_VALIDATION','runtime-validation', '.', f"Runtime check failed: {name}", f"Chạy `{cmd}` và sửa lỗi trước release gate.", {"cmd": cmd, "stderr_tail": res.get('stderr','')[-1500:], "stdout_tail": res.get('stdout','')[-1500:]}))
        return results, findings

    def _detect_commands(self) -> dict[str, str]:
        commands: dict[str, str] = {}
        if (self.repo_root / 'ai_trading_brain').exists() or (self.repo_root / 'backend').exists():
            commands['python_compile'] = "python -m compileall ai_trading_brain backend scripts"
        if (self.repo_root / 'pytest.ini').exists() or (self.repo_root / 'tests').exists():
            commands['pytest'] = "pytest -q"
        if (self.repo_root / 'package.json').exists():
            commands['npm_build'] = "npm run build --if-present"
            commands['npm_lint'] = "npm run lint --if-present"
        if (self.repo_root / 'alembic.ini').exists() or (self.repo_root / 'alembic').exists():
            commands['alembic_heads'] = "alembic heads"
        return commands

    def _run(self, cmd: str) -> dict[str, Any]:
        try:
            p = subprocess.run(cmd, cwd=self.repo_root, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout_seconds)
            return {"cmd": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
        except subprocess.TimeoutExpired as e:
            return {"cmd": cmd, "returncode": 124, "stdout": e.stdout or '', "stderr": f"TIMEOUT after {self.timeout_seconds}s"}
