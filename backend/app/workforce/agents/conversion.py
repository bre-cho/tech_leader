from app.workforce.base import WorkforceAgent
from app.workforce.contracts import WorkforceContext


class ConversionOptimizationAgent(WorkforceAgent):
    name = "ConversionOptimizationAgent"

    def run(self, context: WorkforceContext):
        brief = context.brief
        cta = brief.offer or "Khám phá ngay"
        output = {
            "cta_copy": cta,
            "conversion_path": [
                "capture attention",
                "show product outcome",
                "build trust with proof cue",
                "make CTA obvious",
            ],
            "friction_reducers": ["clear benefit", "simple offer", "visual proof", "no clutter"],
            "primary_kpi": "CTR" if brief.channel in ["tiktok", "facebook", "instagram"] else "conversion_rate",
        }
        context.decisions["conversion"] = output
        return self.ok(output, 0.88)
