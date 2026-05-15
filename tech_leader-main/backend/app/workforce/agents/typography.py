from app.workforce.base import WorkforceAgent
from app.workforce.contracts import WorkforceContext


class TypographyAgent(WorkforceAgent):
    name = "TypographyAgent"

    def run(self, context: WorkforceContext):
        brief = context.brief
        tone = brief.brand_tone.lower()
        industry = brief.industry.lower()

        if "luxury" in tone or "premium" in tone or "fashion" in industry:
            headline = "editorial luxury serif or high-contrast elegant serif"
            body = "clean modern sans-serif"
            spacing = "wide whitespace, premium leading"
        elif "fmcg" in industry or "grooming" in industry:
            headline = "ultra-bold condensed sans-serif"
            body = "bold readable sans-serif"
            spacing = "tight stacked hierarchy, billboard-safe"
        else:
            headline = "bold modern sans-serif"
            body = "clean sans-serif"
            spacing = "clear hierarchy"

        output = {
            "headline_font_logic": headline,
            "body_font_logic": body,
            "spacing": spacing,
            "hierarchy": ["headline", "sub-benefit", "proof", "CTA"],
            "readability_rules": {
                "mobile": "headline readable under 1 second",
                "billboard": "large contrast, no thin text",
                "text_safe_area": "do not cover eyes, logo, or product label",
            },
        }
        context.decisions["typography"] = output
        return self.ok(output, 0.89)
