class ProductHeroEngine:
    def reason(self, product_type: str, industry: str) -> dict:
        p = (product_type or industry).lower()
        mapping = {
            "serum": ("3/4 front glass bottle", ["glass translucency", "gold rim highlights", "liquid clarity"], "near face foreground"),
            "lipstick": ("macro 3/4 metallic tube", ["metal reflection", "sharp lipstick tip", "color payoff"], "near lips"),
            "perfume": ("low angle luxury bottle", ["glass refraction", "mist aura", "metal cap"], "center hero pedestal"),
            "shampoo": ("3/4 FMCG packshot", ["water condensation", "clean white reflection", "label sharpness"], "dominant foreground"),
            "drink": ("cold can/bottle hero", ["condensation", "ice particles", "liquid splash"], "hand-held lifestyle"),
        }
        angle, materials, placement = mapping.get(p, ("3/4 commercial packshot", ["clean reflections", "label clarity", "premium edges"], "foreground hero"))
        return {
            "hero_angle": angle,
            "material_cues": materials,
            "placement": placement,
            "logo_policy": "preserve readable product label; avoid hallucinated brand text if final text is rendered by frontend",
            "packshot_rules": ["no warping", "sharp edges", "consistent perspective", "true scale relative to hand/face"],
        }
