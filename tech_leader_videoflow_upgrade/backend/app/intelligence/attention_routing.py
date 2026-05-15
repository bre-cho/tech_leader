from __future__ import annotations


class AttentionRoutingEngine:
    def build_route(self, category_profile, goal: str):
        route = ["human_face_or_headline", "product_hero", "benefit_proof", "cta"]
        if goal in {"premium_branding", "trust"}:
            route = ["face_or_brand_symbol", "premium_material", "product_hero", "trust_signal", "cta"]
        if category_profile["category"] in {"fmcg", "sports grooming"}:
            route = ["oversized_headline", "cooling_motion", "product_hero", "benefit_claim", "cta"]
        if category_profile["category"] in {"beauty", "cosmetics"}:
            route = ["eyes_and_skin", "product_near_face", "glow_detail", "trust_typography", "cta"]

        return {
            "route": route,
            "dopamine_triggers": [
                "strong focal contrast",
                "micro texture detail",
                "motion cue or particle cue",
                "clear before-after expectation",
            ],
            "retention_triggers": [
                "eye contact or gaze direction",
                "product-face alignment",
                "layered depth",
                "curiosity gap in headline",
            ],
            "conversion_triggers": [
                "clear product visibility",
                "benefit proof near product",
                "CTA with high contrast",
                "offer or outcome promise",
            ],
        }
