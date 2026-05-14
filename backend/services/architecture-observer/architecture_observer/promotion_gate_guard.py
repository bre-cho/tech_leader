from __future__ import annotations
from .models import BlastRadiusReport, DriftReport, PromotionDecision

def promotion_gate(blast: BlastRadiusReport, drift: DriftReport, required_score: int = 85) -> PromotionDecision:
    score, reasons = 100, []
    if blast.risk_level == "critical":
        score -= 45; reasons.append("Critical blast radius.")
    elif blast.risk_level == "high":
        score -= 28; reasons.append("High blast radius.")
    elif blast.risk_level == "medium":
        score -= 12; reasons.append("Medium blast radius.")
    if not drift.passed:
        score -= 35; reasons.append("Architecture drift check failed.")
    if drift.violations:
        score -= min(40, len(drift.violations)*10); reasons.append(f"{len(drift.violations)} layer violations.")
    if drift.warnings:
        score -= min(20, len(drift.warnings)*5); reasons.append(f"{len(drift.warnings)} architecture warnings.")
    score = max(0, score)
    if score >= required_score:
        status = "promote"; reasons.append("Architecture gate passed.")
    elif score >= 65:
        status = "manual_review"; reasons.append("Manual review required before promotion.")
    else:
        status = "block"; reasons.append("Blocked by Architecture Control Tower.")
    return PromotionDecision(status=status, score=score, required_score=required_score, reasons=reasons, blast_radius=blast, drift=drift)
