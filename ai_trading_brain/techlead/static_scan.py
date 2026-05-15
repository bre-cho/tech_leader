from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from .file_inventory import FileInventory
from .models import Finding

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{12,}['\"]"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
]
MOCK_PATTERNS = [re.compile(r"\bTODO\b|\bFIXME\b|mock_|MockDataProvider|NotImplementedError", re.I)]
LIVE_ORDER_HINTS = re.compile(r"\b(order_send|place_order|submit_order|create_order|market_order)\b", re.I)
RISK_GUARD_HINTS = re.compile(r"risk_guard|RiskGuard|preflight|release_gate|allow_execution|max_drawdown", re.I)

class StaticSystemScanner:
    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.inventory = FileInventory(self.repo_root)

    def scan(self) -> list[Finding]:
        findings: list[Finding] = []
        for rec in self.inventory.code_files():
            text = self.inventory.read_text(rec)
            if rec.suffix == ".py":
                findings.extend(self._scan_python(rec.rel, text))
            if rec.suffix == ".json":
                findings.extend(self._scan_json(rec.rel, text))
            findings.extend(self._scan_security(rec.rel, text))
            findings.extend(self._scan_live_trading_safety(rec.rel, text))
            findings.extend(self._scan_mock_leakage(rec.rel, text))
        findings.extend(self._scan_package_integrity())
        return findings

    def _scan_python(self, rel: str, text: str) -> list[Finding]:
        out: list[Finding] = []
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError as e:
            return [Finding("P0", "PHASE_2_STATIC_SYSTEM_SCAN", "syntax", rel, f"Python syntax error: {e.msg} at line {e.lineno}", "Sửa lỗi cú pháp trước mọi runtime validation.", {"line": e.lineno, "offset": e.offset})]
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    if handler.type is None and not any(isinstance(n, ast.Raise) for n in ast.walk(handler)):
                        out.append(Finding("P2", "PHASE_2_STATIC_SYSTEM_SCAN", "logic-drift", rel, "Bare except without re-raise can hide production errors.", "Đổi sang except SpecificError, log structured error, hoặc re-raise.", {"line": handler.lineno}))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                out.append(Finding("P1", "PHASE_2_STATIC_SYSTEM_SCAN", "security-drift", rel, f"Dangerous dynamic execution: {node.func.id}()", "Loại bỏ eval/exec hoặc sandbox rõ ràng.", {"line": node.lineno}))
        return out

    def _scan_json(self, rel: str, text: str) -> list[Finding]:
        try:
            json.loads(text)
            return []
        except json.JSONDecodeError as e:
            return [Finding("P1", "PHASE_2_STATIC_SYSTEM_SCAN", "contract-scan", rel, f"Invalid JSON: {e.msg}", "Sửa JSON để CI/package tooling đọc được.", {"line": e.lineno, "col": e.colno})]

    def _scan_security(self, rel: str, text: str) -> list[Finding]:
        out: list[Finding] = []
        if rel.endswith(".env.example"):
            return out
        for pat in SECRET_PATTERNS:
            m = pat.search(text)
            if m:
                out.append(Finding("P0", "PHASE_2_STATIC_SYSTEM_SCAN", "security-secret", rel, "Potential hard-coded secret/token detected.", "Di chuyển secret sang env/secret manager, rotate key nếu đã commit.", {"match_start": m.start()}))
        return out

    def _scan_live_trading_safety(self, rel: str, text: str) -> list[Finding]:
        if not LIVE_ORDER_HINTS.search(text):
            return []
        if RISK_GUARD_HINTS.search(text):
            return []
        if any(x in rel.lower() for x in ["test_", "/tests/", "mock", "paper"]):
            return []
        return [Finding("P0", "PHASE_2_STATIC_SYSTEM_SCAN", "live-trading-safety", rel, "Order execution function found without obvious Risk Guard / preflight gate.", "Bọc execution bằng RiskGuard + idempotency key + broker reconciliation + release gate trước khi gọi broker thật.")]

    def _scan_mock_leakage(self, rel: str, text: str) -> list[Finding]:
        if any(x in rel.lower() for x in ["test_", "/tests/", "docs/", "readme", ".md"]):
            return []
        if rel.startswith("backend/") or rel.startswith("ai_trading_brain/"):
            for pat in MOCK_PATTERNS:
                if pat.search(text):
                    return [Finding("P2", "PHASE_2_STATIC_SYSTEM_SCAN", "mock-leakage", rel, "Mock/TODO/FIXME/NotImplemented marker appears in production path.", "Đưa mock sang tests/adapters hoặc cấu hình rõ PAPER/LIVE mode.")]
        return []

    def _scan_package_integrity(self) -> list[Finding]:
        out: list[Finding] = []
        for p in self.repo_root.rglob("*.py"):
            if any(skip in p.parts for skip in {".venv", "venv", "node_modules", "__pycache__"}):
                continue
            parent = p.parent
            if parent == self.repo_root:
                continue
            if any(part in {"tests", "scripts"} for part in parent.parts):
                continue
            init = parent / "__init__.py"
            if not init.exists() and any(anchor in parent.parts for anchor in {"ai_trading_brain", "backend", "app", "apps"}):
                rel = str(parent.relative_to(self.repo_root)).replace("\\", "/")
                out.append(Finding("P2", "PHASE_2_STATIC_SYSTEM_SCAN", "import-export", rel, "Python package directory lacks __init__.py.", "Tạo __init__.py để import ổn định trong CI/runtime."))
        return out
