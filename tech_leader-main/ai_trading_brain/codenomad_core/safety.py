from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Literal

RiskLevel = Literal["low", "medium", "high", "blocked"]

BLOCKED_PATTERNS = [
    "rm -rf /", "rm -rf ~", "mkfs", "dd if=", ":(){", "shutdown", "reboot",
    "curl | sh", "wget | sh", "sudo rm", "chmod -R 777 /", "git push --force",
]
HIGH_PATTERNS = ["rm -rf", "drop table", "truncate", "delete from", "sudo ", "docker system prune", "kubectl delete", "terraform apply"]
MEDIUM_PATTERNS = ["pip install", "npm install", "pnpm install", "yarn add", "alembic upgrade", "prisma migrate", "docker compose up"]
LOW_PREFIXES = ["python", "python3", "pytest", "ruff", "mypy", "npm test", "npm run", "pnpm test", "pnpm run", "node", "bash scripts", "git status", "git diff", "ls", "find"]


@dataclass(slots=True)
class CommandRisk:
    level: RiskLevel
    reason: str
    requires_approval: bool


def classify_command(command: str) -> CommandRisk:
    c = command.strip().lower()
    if not c:
        return CommandRisk("blocked", "empty command", True)
    if any(p in c for p in BLOCKED_PATTERNS):
        return CommandRisk("blocked", "destructive/system-level pattern detected", True)
    if any(p in c for p in HIGH_PATTERNS):
        return CommandRisk("high", "high-impact command requires explicit approval", True)
    if any(p in c for p in MEDIUM_PATTERNS):
        return CommandRisk("medium", "dependency/runtime mutation requires approval", True)
    if any(c.startswith(p) for p in LOW_PREFIXES):
        return CommandRisk("low", "safe validation/developer command", False)
    try:
        first = shlex.split(command)[0]
    except Exception:
        first = command.split()[0]
    if first in {"cat", "sed", "grep", "pwd", "echo"}:
        return CommandRisk("low", "read-only shell command", False)
    return CommandRisk("medium", "unknown command category", True)
