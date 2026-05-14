from typing import Dict, Any
from app.config import settings

class CommercialPromptCompiler:
    def compile(self, req: Dict[str, Any], reasoning: Dict[str, Any]) -> Dict[str, Any]:
        psych = reasoning["psychology"]
        category_rules = ", ".join(reasoning["category"]["category_rules"])
        attention_order = " → ".join(reasoning["attention"]["visual_attention_order"])
        reactions = ", ".join(reasoning["environment"]["environment_reactions"])
        material = ", ".join(reasoning["product_hero"]["material_logic"])
        prompt = (
            f"Premium commercial advertising visual for {req['product_or_service']} in {req['industry']} category. "
            f"Business goal: {req['business_goal']}. Target audience: {req['audience']}. "
            f"Attention routing order: {attention_order}. "
            f"Commercial psychology: evoke {psych['emotion']}, create {psych['perception']}, trigger {psych['buying_trigger']}. "
            f"Product hero: {reasoning['product_hero']['hero_angle']}, material fidelity: {material}. "
            f"Typography: {reasoning['typography']['font_logic']}, safe readable hierarchy, clean CTA zone. "
            f"Environment reacts naturally: {reactions}. "
            f"Category rules: {category_rules}. "
            f"Ultra realistic, cinematic commercial lighting, sharp texture, premium reflections, 8K-ready, no distorted text."
        )
        negative = (
            "distorted hands, distorted face, unreadable text, warped logo, plastic skin, over-smoothed texture, "
            "bad anatomy, low resolution, muddy colors, cluttered layout, weak product visibility"
        )
        return {
            "prompt": prompt,
            "negative_prompt": negative,
            "provider": req.get("constraints", {}).get("provider", settings.hidream_provider),
            "aspect_ratio": req.get("constraints", {}).get("aspect_ratio", "4:5"),
            "quality": "premium_8k_ready"
        }
