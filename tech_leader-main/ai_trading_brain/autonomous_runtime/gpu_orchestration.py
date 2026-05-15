from __future__ import annotations

class GPUOrchestrator:
    def plan(self, workload: str, gpu_available: bool = False) -> dict:
        mode = "gpu" if gpu_available else "cpu_fallback"
        return {"workload": workload, "mode": mode, "queue": "gpu-high" if gpu_available else "cpu-default", "policy": "fallback-safe"}
