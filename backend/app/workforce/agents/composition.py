from app.workforce.base import WorkforceAgent
from app.workforce.contracts import WorkforceContext


class CompositionAgent(WorkforceAgent):
    name = "CompositionAgent"

    def run(self, context: WorkforceContext):
        regions = [
            {
                "name": "emotional_anchor",
                "priority": 1,
                "purpose": "face, body language, or emotional hook",
                "bbox": {"x": 0.06, "y": 0.08, "w": 0.40, "h": 0.45},
                "rules": ["avoid cropping eyes", "expression must match product promise"],
            },
            {
                "name": "product_hero",
                "priority": 2,
                "purpose": "product desire and label recognition",
                "bbox": {"x": 0.52, "y": 0.18, "w": 0.36, "h": 0.42},
                "rules": ["label readable", "3/4 angle", "lighting matches scene"],
            },
            {
                "name": "typography",
                "priority": 3,
                "purpose": "headline and benefit hierarchy",
                "bbox": {"x": 0.08, "y": 0.58, "w": 0.82, "h": 0.18},
                "rules": ["max 2 benefit lines", "high contrast", "mobile readability"],
            },
            {
                "name": "cta",
                "priority": 4,
                "purpose": "conversion action",
                "bbox": {"x": 0.52, "y": 0.80, "w": 0.36, "h": 0.12},
                "rules": ["tap-safe", "high contrast", "clear offer"],
            },
        ]
        context.canvas_regions = regions
        output = {
            "canvas_regions": regions,
            "visual_balance": "emotional anchor and product hero use diagonal attention flow",
            "spacing_rule": "preserve negative space around product and typography",
        }
        context.decisions["composition"] = output
        return self.ok(output, 0.91)
