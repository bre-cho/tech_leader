from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal
import json

TaskStatus = Literal["queued", "running", "completed", "failed", "blocked"]

@dataclass(frozen=True)
class AgentTask:
    task_id: str
    role: str
    goal: str
    resources: dict = field(default_factory=dict)

@dataclass(frozen=True)
class ExecutionResult:
    task_id: str
    status: TaskStatus
    output: str
    worker: str

@dataclass(frozen=True)
class AutonomousRuntimeReport:
    swarm_plan: list[AgentTask]
    distributed_results: list[ExecutionResult]
    gpu_plan: dict
    cloud_plan: dict

    def write_json(self, path: str | Path) -> Path:
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        return out
