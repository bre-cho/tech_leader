from dataclasses import dataclass
from typing import Any, Optional

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

    def __init__(self, decision_logger=None):
        self._logger = decision_logger

    def validate_trace(self, trace: dict[str, bool], workflow_id: str = "unknown") -> LawDecision:
        missing = [step for step in REQUIRED_LAW_STEPS if not trace.get(step)]
        passed = not missing
        decision = LawDecision(
            passed,
            "PASSED" if passed else "BLOCKED",
            missing,
            "Operating law satisfied" if passed else "Operating law violation: missing required lifecycle steps",
        )
        if self._logger is not None:
            self._logger.log(
                workflow_id=workflow_id,
                decision_type="operating_law.validate_trace",
                outcome=decision.status,
                reason=decision.message,
                metadata={"missing_steps": missing},
            )
        return decision

    def build_default_trace(self) -> dict[str, bool]:
        return {step: False for step in REQUIRED_LAW_STEPS}

    def assert_can_promote(self, trace: dict[str, bool], verification: dict[str, Any], workflow_id: str = "unknown") -> dict[str, Any]:
        law = self.validate_trace(trace, workflow_id=workflow_id)
        checks = verification.get("checks", {}).copy() if verification else {}
        checks["operating_law"] = law.passed
        failed_checks = [k for k, v in checks.items() if not v]
        passed = law.passed and not failed_checks
        result = {
            "status": "PASSED" if passed else "BLOCKED",
            "passed": passed,
            "law_status": law.status,
            "missing_law_steps": law.missing_steps,
            "failed_verification_checks": failed_checks,
            "rule": "NO VERIFY → NO PROMOTION; NO MEMORY → NO SCALE; NO WINNER DNA → NO OPTIMIZATION",
        }
        if self._logger is not None:
            self._logger.log(
                workflow_id=workflow_id,
                decision_type="operating_law.assert_can_promote",
                outcome=result["status"],
                reason=f"failed_checks={failed_checks}" if not passed else "all checks passed",
                metadata={"failed_checks": failed_checks, "missing_steps": law.missing_steps},
            )
        return result
