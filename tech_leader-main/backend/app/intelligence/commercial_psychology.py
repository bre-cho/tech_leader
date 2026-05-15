from __future__ import annotations


class CommercialPsychologyEngine:
    def map(self, category_profile):
        category = category_profile["category"]
        mapping = {
            "fmcg": {
                "freshness": "daily functional benefit",
                "white reflections": "clinical trust",
                "high contrast": "shelf visibility",
            },
            "sports grooming": {
                "cold freshness": "anti-dandruff / menthol sensation",
                "blue energy": "performance grooming",
                "metallic gradients": "premium FMCG",
            },
            "beauty": {
                "warm glow": "healthy skin trust",
                "soft champagne": "luxury femininity",
                "natural texture": "authentic beauty proof",
            },
            "cosmetics": {
                "macro texture": "desire and product payoff",
                "editorial lighting": "premium confidence",
                "face-product alignment": "try-on intent",
            },
            "luxury branding": {
                "negative space": "status",
                "black/gold": "premium exclusivity",
                "controlled light": "expensive perception",
            },
        }
        return mapping.get(category, {
            "clarity": "purchase confidence",
            "product dominance": "decision support",
            "clean CTA": "conversion readiness",
        })
