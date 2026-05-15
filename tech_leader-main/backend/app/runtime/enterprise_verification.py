from __future__ import annotations

from app.core.contracts import VerificationReport, VisualDecision


class VerificationEngine:
    def verify(self, decision: VisualDecision, prompt: str):
        checks = {
            "attention_route_exists": len(decision.attention_route) >= 4,
            "dopamine_triggers_exists": len(decision.dopamine_triggers) >= 3,
            "trust_triggers_exists": len(decision.trust_triggers) >= 2,
            "conversion_triggers_exists": len(decision.conversion_triggers) >= 3,
            "typography_rules_exists": bool(decision.typography_plan.get("readability_rules")),
            "product_hero_exists": bool(decision.product_hero_plan.get("angle")),
            "environment_reaction_exists": bool(decision.environment_reaction_plan.get("reaction_type")),
            "commercial_psychology_exists": bool(decision.commercial_psychology),
            "print_plan_exists": bool(decision.print_export_plan.get("exports")),
            "prompt_is_not_generic": "COMMERCIAL VISUAL REASONING" in prompt and "PRODUCT HERO ENGINE" in prompt,
        }
        score = round(sum(1 for v in checks.values() if v) / len(checks) * 100, 2)
        issues = [k for k, v in checks.items() if not v]
        return VerificationReport(passed=score >= 85, score=score, checks=checks, issues=issues)
