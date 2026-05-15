from app.agents.base import BaseAgent

class ImageQAAgent(BaseAgent):
    name = "image-qa-agent"
    required_inputs = ["image_concepts", "business_diagnosis"]

    def execute(self, context):
        diag = context["business_diagnosis"]
        out = []
        for concept in context["image_concepts"]:
            base = 78
            vt = concept["visual_type"]
            attention = base + (10 if vt in ["viral", "premium"] else 6)
            trust = base + (10 if vt in ["trust", "premium"] else 5)
            conversion = base + (11 if vt == "conversion" else 7)
            brand_fit = base + (9 if "premium" in concept["layout_direction"] else 6)
            video_potential = base + (12 if diag["upsell_potential"] == "high" else 7) + (3 if vt in ["viral", "premium"] else 0)
            concept["score"] = {
                "attention_score": min(attention, 99),
                "trust_score": min(trust, 99),
                "conversion_score": min(conversion, 99),
                "brand_fit_score": min(brand_fit, 99),
                "upsell_video_potential_score": min(video_potential, 99),
                "video_upsell_ready": video_potential >= 85,
                "rationale": "Strong hook, clear value proposition, and enough motion potential for video upsell.",
            }
            out.append(concept)
        return out
