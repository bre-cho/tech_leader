from dataclasses import dataclass
from typing import Any

CORE_OPERATING_LAW = """
USER INPUT → TECHNICAL LEAD AGENT → PLANNER → CAPABILITY ROUTER → SPECIALIZED AGENTS
→ EXECUTION MANAGER → VERIFICATION ENGINE → PROMOTION GATE → MEMORY UPDATE → WINNER DNA ENGINE

Mọi tính năng mới bắt buộc đi qua: Workflow → Agent → Skill → Runtime → Verify → Memory → Winner DNA.
NO WORKFLOW → NO BUILD. NO VERIFY → NO PROMOTION. NO MEMORY → NO SCALE.
""".strip()

REQUIRED_LAW_STEPS = [
    "target_define",
    "research",
    "plan",
    "execute",
    "verify",
    "distill_to_skill",
    "memory_update",
    "winner_dna_update",
]

REQUIRED_CONTEXT_ENTITIES = [
    "BusinessEntity",
    "AudienceEntity",
    "CreativeEntity",
    "PosterEntity",
    "VideoEntity",
    "StoryboardEntity",
    "OfferEntity",
    "CampaignEntity",
    "AnalyticsEntity",
    "WinnerDNAEntity",
]

@dataclass
class LawDecision:
    passed: bool
    status: str
    missing_steps: list[str]
    message: str

class OperatingLawEnforcer:
    """Non-bypassable governance layer for every workflow/feature."""

    def validate_trace(self, trace: dict[str, bool]) -> LawDecision:
        missing = [step for step in REQUIRED_LAW_STEPS if not trace.get(step)]
        if missing:
            return LawDecision(False, "BLOCKED", missing, "Operating law violation: missing required lifecycle steps")
        return LawDecision(True, "PASSED", [], "Operating law satisfied")

    def build_default_trace(self) -> dict[str, bool]:
        return {step: False for step in REQUIRED_LAW_STEPS}

    def assert_can_promote(self, trace: dict[str, bool], verification: dict[str, Any]) -> dict[str, Any]:
        law = self.validate_trace(trace)
        checks = verification.get("checks", {}) if verification else {}
        failed_checks = [k for k, v in checks.items() if not v]
        passed = law.passed and not failed_checks
        return {
            "status": "PASSED" if passed else "BLOCKED",
            "passed": passed,
            "law_status": law.status,
            "missing_law_steps": law.missing_steps,
            "failed_verification_checks": failed_checks,
            "rule": "NO VERIFY → NO PROMOTION; NO MEMORY → NO SCALE; NO WINNER DNA → NO OPTIMIZATION",
        }
