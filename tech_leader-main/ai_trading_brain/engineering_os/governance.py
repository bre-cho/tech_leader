from __future__ import annotations

from .models import GovernanceDecision, PhasePlan, RiskLevel

CRITICAL_PATTERNS = ["delete", "drop table", "truncate", "production secret", "disable auth"]
HIGH_PATTERNS = ["migration", "database", "payment", "auth", "security", "deploy", "worker"]


def evaluate_phase_plan(plan: PhasePlan) -> GovernanceDecision:
    text = " ".join([plan.task, plan.migration_impact, *plan.files_to_modify, *plan.risks]).lower()
    if any(p in text for p in CRITICAL_PATTERNS):
        return GovernanceDecision(
            status="blocked",
            risk_level="critical",
            reasons=["Critical destructive or security-sensitive action detected"],
            required_approvals=["Human owner", "Security reviewer"],
            blocked_actions=["Do not execute until task is decomposed and explicitly approved"],
        )
    if plan.approval_required or any(p in text for p in HIGH_PATTERNS):
        return GovernanceDecision(
            status="needs_human_approval",
            risk_level="high",
            reasons=["High-risk area detected: schema/auth/security/deployment/worker impact"],
            required_approvals=["Human owner"],
            blocked_actions=["No production deploy", "No irreversible migration", "No secret changes"],
        )
    return GovernanceDecision(
        status="approved",
        risk_level="medium" if plan.files_to_modify else "low",
        reasons=["Plan is additive and no critical governance trigger was detected"],
        required_approvals=[],
        blocked_actions=[],
    )
