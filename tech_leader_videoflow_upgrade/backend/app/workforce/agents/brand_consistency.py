from app.workforce.base import WorkforceAgent
from app.workforce.contracts import WorkforceContext


class BrandConsistencyAgent(WorkforceAgent):
    name = "BrandConsistencyAgent"

    def run(self, context: WorkforceContext):
        brief = context.brief
        tone = brief.brand_tone.lower()
        industry = brief.industry.lower()

        if "beauty" in industry or "spa" in industry:
            colors = ["champagne", "ivory", "warm beige", "soft gold"]
            language = ["soft glow", "premium skin", "clean beauty", "trust warmth"]
        elif "fashion" in industry:
            colors = ["black", "ivory", "editorial gray", "champagne"]
            language = ["editorial", "silhouette", "fabric realism", "luxury space"]
        elif "fmcg" in industry or "grooming" in industry:
            colors = ["electric blue", "white", "metallic silver", "deep navy"]
            language = ["freshness", "energy", "cooling", "readable packshot"]
        else:
            colors = ["deep navy", "white", "silver", "accent color"]
            language = ["clarity", "trust", "modern product hero"]

        if "luxury" in tone:
            colors = ["black", "champagne gold", "ivory", "soft shadow"]

        design_system = {
            "colors": colors,
            "visual_language": language,
            "logo_rules": ["keep logo readable", "do not distort", "place in low-conflict zone"],
            "brand_tone": brief.brand_tone,
        }
        context.design_system.update(design_system)
        context.decisions["brand_consistency"] = design_system
        return self.ok(design_system, 0.9)
