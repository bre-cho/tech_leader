from __future__ import annotations

from pathlib import Path

from .file_inventory import FileInventory
from .models import Finding

class SafeAutoFixer:
    """Conservative auto-fix only. Never changes trading strategy logic automatically."""

    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.inventory = FileInventory(self.repo_root)

    def apply(self) -> list[Finding]:
        fixed: list[Finding] = []
        fixed.extend(self._ensure_package_inits())
        fixed.extend(self._normalize_text_files())
        fixed.extend(self._ensure_runtime_dirs())
        fixed.extend(self._ensure_agent16_command_files())
        return fixed

    def _ensure_package_inits(self) -> list[Finding]:
        fixed: list[Finding] = []
        for base in ["ai_trading_brain", "backend", "apps/api/app"]:
            root = self.repo_root / base
            if not root.exists():
                continue
            dirs = [root, *[p for p in root.rglob("*") if p.is_dir()]]
            for d in dirs:
                if any(x in d.parts for x in {"__pycache__", "tests", "node_modules"}):
                    continue
                if list(d.glob("*.py")):
                    init = d / "__init__.py"
                    if not init.exists():
                        init.write_text("", encoding="utf-8")
                        rel = str(init.relative_to(self.repo_root)).replace("\\", "/")
                        fixed.append(Finding("INFO", "PHASE_6_SAFE_AUTOFIX", "safe-autofix", rel, "Created missing __init__.py.", "Đã tạo để ổn định import."))
        return fixed

    def _normalize_text_files(self) -> list[Finding]:
        fixed: list[Finding] = []
        for rec in self.inventory.code_files():
            if rec.size > 750_000:
                continue
            text = self.inventory.read_text(rec)
            if not text:
                continue
            normalized = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
            if not normalized.endswith("\n"):
                normalized += "\n"
            if normalized != text:
                rec.path.write_text(normalized, encoding="utf-8")
                fixed.append(Finding("INFO", "PHASE_6_SAFE_AUTOFIX", "safe-autofix", rec.rel, "Normalized line endings/trailing whitespace.", "Không thay đổi logic."))
        return fixed

    def _ensure_runtime_dirs(self) -> list[Finding]:
        fixed: list[Finding] = []
        for d in ["reports", "context_graph", ".ai-workforce/commands", "docs/ai_tech_lead_os"]:
            p = self.repo_root / d
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
                fixed.append(Finding("INFO", "PHASE_6_SAFE_AUTOFIX", "safe-autofix", d, "Created runtime directory.", "Dùng cho audit reports/context graph."))
        return fixed

    def _ensure_agent16_command_files(self) -> list[Finding]:
        fixed: list[Finding] = []
        cmd = self.repo_root / ".ai-workforce/commands/AGENT16_AUDIT.md"
        if not cmd.exists():
            cmd.parent.mkdir(parents=True, exist_ok=True)
            cmd.write_text(
                "# AGENT16_AUDIT\n\nRun:\n\n```bash\npython scripts/agent16_audit.py . --runtime --apply-safe-fixes --out reports/agent16_audit_report.md\n```\n\nRules: fix P0 first, then P1, never bypass Risk Guard for live trading.\n",
                encoding="utf-8",
            )
            fixed.append(Finding("INFO", "PHASE_6_SAFE_AUTOFIX", "safe-autofix", ".ai-workforce/commands/AGENT16_AUDIT.md", "Created Agent 16 command file.", "Claude/Cursor/Copilot can reuse this."))
        return fixed
