from __future__ import annotations

from typing import Any


class CTARecommendationService:
    def recommend(self, content_goal: str, conversion_mode: str) -> str:
        templates = {
            "awareness": {
                "soft": "Learn more about our {niche} solution",
                "direct": "Get started with {niche} today",
            },
            "engagement": {
                "soft": "Discover {niche} insights",
                "direct": "Join {niche} community now",
            },
            "conversion": {
                "soft": "See how {niche} works",
                "direct": "Buy {niche} today - limited time",
            },
        }
        mode_dict = templates.get(content_goal or "engagement", templates["engagement"])
        cta_type = conversion_mode or "soft"
        return mode_dict.get(cta_type, "Explore more")
