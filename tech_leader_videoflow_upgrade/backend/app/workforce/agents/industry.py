from app.workforce.base import WorkforceAgent
from app.workforce.contracts import WorkforceContext


class IndustryIntelligenceAgent(WorkforceAgent):
    name = "IndustryIntelligenceAgent"

    def run(self, context: WorkforceContext):
        industry = context.brief.industry.lower()
        playbooks = {
            "beauty": ["skin trust", "glow proof", "texture realism", "soft luxury"],
            "cosmetics": ["try-on intent", "face-product alignment", "color payoff", "editorial beauty"],
            "spa": ["relaxation", "warmth", "clean wellness", "premium calm"],
            "fashion": ["silhouette", "fabric physics", "pose", "editorial confidence"],
            "f&b": ["appetite", "macro texture", "warmth", "freshness"],
            "real estate": ["space depth", "trust", "lighting", "premium lifestyle"],
        }
        matched = []
        for key, value in playbooks.items():
            if key in industry:
                matched = value
                break
        if not matched:
            matched = ["clarity", "trust", "product value", "conversion"]

        output = {"industry_playbook": matched, "adaptation_rule": "all agents must respect category psychology"}
        context.decisions["industry"] = output
        return self.ok(output, 0.87)
