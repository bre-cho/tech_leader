from app.workforce.base import WorkforceAgent
from app.workforce.contracts import WorkforceContext


class MotionThinkingAgent(WorkforceAgent):
    name = "MotionThinkingAgent"

    def run(self, context: WorkforceContext):
        strategy = context.decisions.get("visual_strategy", {})
        route = strategy.get("attention_route", ["hook", "product", "proof", "CTA"])
        storyboard = [
            {"scene": 1, "title": "Hook", "visual": route[0], "duration_sec": 2},
            {"scene": 2, "title": "Product Movement", "visual": "product enters frame; gaze/body language follows product", "duration_sec": 3},
            {"scene": 3, "title": "Benefit Proof", "visual": route[2] if len(route) > 2 else "proof detail", "duration_sec": 3},
            {"scene": 4, "title": "CTA", "visual": "brand + offer + clear action", "duration_sec": 2},
        ]
        output = {
            "poster_to_video_logic": "motion routes attention from human emotion to product hero to CTA",
            "storyboard": storyboard,
            "body_language_rules": [
                "eyes follow product movement",
                "smile appears after product benefit is revealed",
                "hands gesture naturally toward product",
                "avoid static presenter posture",
            ],
        }
        context.decisions["motion"] = output
        return self.ok(output, 0.9)
