from __future__ import annotations
from pathlib import Path
from .agent_swarm import AgentSwarmPlanner
from .distributed_execution import DistributedExecutor
from .gpu_orchestration import GPUOrchestrator
from .cloud_native_runtime import CloudNativeRuntimePlanner
from .models import AutonomousRuntimeReport

class AutonomousRuntime:
    def run(self, goal: str, gpu_available: bool = False, output_path: str | Path = "docs/runtime/autonomous-runtime-report.json") -> AutonomousRuntimeReport:
        tasks = AgentSwarmPlanner().plan(goal)
        results = DistributedExecutor().execute(tasks)
        gpu = GPUOrchestrator().plan(goal, gpu_available=gpu_available)
        cloud = CloudNativeRuntimePlanner().plan("agent16-autonomous-runtime")
        report = AutonomousRuntimeReport(tasks, results, gpu, cloud)
        report.write_json(output_path)
        return report
