from __future__ import annotations


class PromotionGate:
    def decide(self, verification, business):
        if not verification.passed:
            return "BLOCKED_BY_VERIFICATION"
        if verification.score >= 92:
            return "PROMOTED_TO_WINNER_DNA_CANDIDATE"
        return "APPROVED_FOR_PREVIEW"
