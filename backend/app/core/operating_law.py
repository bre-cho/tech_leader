from __future__ import annotations

from typing import Any


CORE_OPERATING_LAW = {
    "system_identity": "AI-Native Creative Business Infrastructure",
    "forbidden": [
        "feature_first_development",
        "isolated_generators",
        "memoryless_execution",
        "ungoverned_runtime",
        "non_verifiable_outputs",
    ],
    "required_pipeline": [
        "TARGET_DEFINE",
        "RESEARCH",
        "PLAN",
        "EXECUTE",
        "VERIFY",
        "DISTILL_TO_SKILL",
        "MEMORY_UPDATE",
        "WINNER_DNA_UPDATE",
    ],
    "architecture_flow": [
        "USER_INPUT",
        "TECHNICAL_LEAD_AGENT",
        "PLANNER",
        "CAPABILITY_ROUTER",
        "SPECIALIZED_AGENTS",
        "EXECUTION_MANAGER",
        "VERIFICATION_ENGINE",
        "PROMOTION_GATE",
        "MEMORY_UPDATE",
        "WINNER_DNA_ENGINE",
    ],
    "build_model": [
        "workflow_first",
        "agent_driven",
        "memory_backed",
        "revenue_optimized",
        "verification_gated",
        "winner_dna_powered",
    ],
}


class CoreOperatingLaw:
    def __init__(self):
        self.required_pipeline = CORE_OPERATING_LAW["required_pipeline"]

    def validate_stages(self, stages: list[Any]) -> dict[str, Any]:
        completed = []
        for stage in stages:
            value = getattr(stage, "value", stage)
            completed.append(str(value))
        missing = [s for s in self.required_pipeline if s not in completed]
        return {
            "passed": not missing,
            "missing_steps": missing,
            "blocked": bool(missing),
            "reason": "NO_WORKFLOW_OR_VERIFY_OR_MEMORY_NO_PROMOTION" if missing else "PASSED",
        }


def enforce_required_pipeline(trace: dict) -> dict:
    missing = [s for s in CORE_OPERATING_LAW["required_pipeline"] if s not in trace.get("completed_steps", [])]
    return {
        "passed": not missing,
        "missing_steps": missing,
        "blocked": bool(missing),
        "reason": "NO_WORKFLOW_OR_VERIFY_OR_MEMORY_NO_PROMOTION" if missing else "PASSED",
    }
