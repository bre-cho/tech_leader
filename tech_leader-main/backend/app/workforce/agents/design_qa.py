from app.workforce.base import WorkforceAgent
from app.workforce.contracts import WorkforceContext


class DesignQAAgent(WorkforceAgent):
    name = "DesignQAAgent"

    def run(self, context: WorkforceContext):
        decisions = context.decisions
        checks = {
            "has_creative_direction": "creative_direction" in decisions,
            "has_visual_strategy": "visual_strategy" in decisions,
            "has_composition": "composition" in decisions,
            "has_typography": "typography" in decisions,
            "has_brand_consistency": "brand_consistency" in decisions,
            "has_conversion": "conversion" in decisions,
            "has_motion": "motion" in decisions,
            "has_industry": "industry" in decisions,
            "product_region_exists": any(r.get("name") == "product_hero" for r in context.canvas_regions),
            "cta_region_exists": any(r.get("name") == "cta" for r in context.canvas_regions),
        }
        context.qa_checks.update(checks)
        score = sum(1 for v in checks.values() if v) / len(checks) * 100
        warnings = [k for k, v in checks.items() if not v]
        output = {
            "score": round(score, 2),
            "checks": checks,
            "qa_gate": "pass" if score >= 90 else "blocked",
            "warnings": warnings,
        }
        return self.ok(output, score / 100, warnings)
