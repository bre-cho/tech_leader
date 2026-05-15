from app.workforce.base import WorkforceAgent
from app.workforce.contracts import WorkforceContext


class CreativeDirectorAgent(WorkforceAgent):
    name = "CreativeDirectorAgent"

    def run(self, context: WorkforceContext):
        brief = context.brief
        goal_map = {
            "conversion": "drive immediate product desire and low-friction action",
            "awareness": "make the brand instantly memorable",
            "trust": "build confidence through proof, clarity, and premium restraint",
            "premium_branding": "elevate perceived value and category authority",
        }
        direction = goal_map.get(brief.campaign_goal, "create a strong commercial visual")
        output = {
            "creative_direction": direction,
            "single_big_idea": f"{brief.product_name} becomes the hero solution for {brief.target_audience}",
            "must_have": [
                "clear product hero",
                "emotion-first visual hook",
                "brand-consistent color and typography",
                "CTA after trust/value is established",
            ],
            "avoid": ["generic AI poster", "overcrowded layout", "unreadable text", "fake product details"],
        }
        context.decisions["creative_direction"] = output
        return self.ok(output, 0.92)
