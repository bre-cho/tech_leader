from __future__ import annotations
from .models import AgentTask, ExecutionResult

class DistributedExecutor:
    def execute(self, tasks: list[AgentTask]) -> list[ExecutionResult]:
        results = []
        for index, task in enumerate(tasks):
            worker = f"local-worker-{index % 2 + 1}"
            results.append(ExecutionResult(task.task_id, "completed", f"Simulated execution: {task.goal}", worker))
        return results
