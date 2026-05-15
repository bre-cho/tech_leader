from app.agents.base import BaseAgent

class ImageDesignAgent(BaseAgent):
    name = "image-design-agent"
    required_inputs = ["request", "business_diagnosis"]

    def _mechanism(self, industry: str, product: str):
        text = f"{industry} {product}".lower()
        if any(k in text for k in ["spa", "mỹ phẩm", "serum", "skincare", "beauty"]):
            return {"type": "beauty_transformation", "proof": "before_after_glow", "emotion": "confidence_trust"}
        if any(k in text for k in ["f&b", "food", "cafe", "nhà hàng", "trà", "bánh"]):
            return {"type": "sensory_appetite", "proof": "closeup_texture", "emotion": "craving"}
        if any(k in text for k in ["bất động sản", "real estate", "villa", "căn hộ"]):
            return {"type": "cinematic_space_tour", "proof": "location_lifestyle", "emotion": "aspiration"}
        return {"type": "problem_solution", "proof": "benefit_visual", "emotion": "trust_action"}

    def execute(self, context):
        req = context["request"]
        diag = context["business_diagnosis"]
        recalled = context.get("recalled_winner_dna", [])
        mechanism = self._mechanism(req.industry, req.product)
        winner_hint = recalled[0]["hook"] if recalled else ""
        concepts = []
        variants = [
            ("trust", "Bằng chứng đáng tin", "clean trust layout, testimonial/proof zone, premium lighting"),
            ("viral", "Dừng lại 3 giây", "bold hook, dynamic contrast, social-first composition"),
            ("conversion", "Ưu đãi hôm nay", "offer-first layout, CTA button area, product hero foreground"),
            ("premium", "Nâng cấp trải nghiệm", "luxury editorial style, cinematic depth, refined typography space"),
        ]
        for i, (variant, headline_seed, layout) in enumerate(variants, start=1):
            headline = winner_hint if i == 1 and winner_hint else f"{headline_seed}: {req.product} cho {req.audience}"
            prompt = (
                f"Create a premium commercial advertising poster for {req.brand_name or req.product}, "
                f"industry: {req.industry}, product/service: {req.product}, target audience: {req.audience}. "
                f"Core pain point: {diag['pain_point']}. Selling angle: {diag['selling_angle']}. "
                f"Mechanism: {mechanism['type']} with proof {mechanism['proof']} and emotion {mechanism['emotion']}. "
                f"Layout: {layout}. Tone: {req.tone}. 4:5 vertical poster, cinematic lighting, "
                "clear typography area, realistic details, premium brand finish, no watermark, no distorted text."
            )
            concepts.append({
                "concept_id": f"IMG-{i:02d}-{variant.upper()}",
                "headline": headline,
                "cta": "Nhận tư vấn ngay" if req.language == "vi" else "Get started today",
                "visual_type": variant,
                "layout_direction": layout,
                "prompt": prompt,
                "negative_prompt": "low quality, blurry, distorted text, watermark, extra limbs, cheap layout",
                "provider_contract": {
                    "preferred_models": ["gpt-image-1", "stable-diffusion", "midjourney-compatible"],
                    "aspect_ratio": "4:5",
                    "quality": "8k ultra high resolution, cinematic commercial quality",
                    "safe_text_policy": "generate clean typography area; render final text in frontend when possible",
                },
                "selling_mechanism": mechanism,
            })
        return concepts
