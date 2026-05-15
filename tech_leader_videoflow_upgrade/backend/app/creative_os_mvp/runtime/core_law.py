from dataclasses import dataclass
from typing import Iterable

REQUIRED_PIPELINE = [
    "TARGET_DEFINE",
    "RESEARCH",
    "PLAN",
    "EXECUTE",
    "VERIFY",
    "DISTILL_TO_SKILL",
    "MEMORY_UPDATE",
    "WINNER_DNA_UPDATE",
]

@dataclass
class LawResult:
    passed: bool
    missing: list[str]
    message: str

class CoreOperatingLaw:
    """Non-bypassable law for every feature/workflow execution."""
    def validate(self, stages: Iterable[str]) -> LawResult:
        stage_set = set(stages)
        missing = [s for s in REQUIRED_PIPELINE if s not in stage_set]
        if missing:
            return LawResult(False, missing, f"PROMOTION_GATE=BLOCKED. Missing stages: {missing}")
        return LawResult(True, [], "Core Operating Law satisfied")

    def assert_feature_contract(self, feature_manifest: dict) -> LawResult:
        required_keys = ["workflow", "agents", "runtime", "verification", "memory_hooks", "docs", "tests"]
        missing = [k for k in required_keys if not feature_manifest.get(k)]
        if missing:
            return LawResult(False, missing, f"FEATURE_REJECTED. Missing contract keys: {missing}")
        return LawResult(True, [], "Feature contract accepted")
