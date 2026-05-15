from __future__ import annotations

class CloudNativeRuntimePlanner:
    def plan(self, service_name: str) -> dict:
        return {
            "service": service_name,
            "container": {"healthcheck": "/health", "restart_policy": "on-failure"},
            "scaling": {"min_replicas": 1, "max_replicas": 5, "metric": "queue_depth"},
            "observability": ["structured_logs", "metrics", "runtime_report"],
        }
