from __future__ import annotations


class TypographyHierarchyEngine:
    def plan(self, channel: str, category: str, brand_tone: str):
        billboard = channel == "billboard"
        tiktok = channel == "tiktok"

        headline_style = "ultra-bold condensed sans-serif" if category in {"fmcg", "sports grooming"} else "elegant high-contrast serif + clean sans-serif"
        if "luxury" in brand_tone.lower() or category == "luxury branding":
            headline_style = "editorial luxury serif, high whitespace, premium spacing"

        return {
            "headline_style": headline_style,
            "hierarchy": ["headline", "visual hero", "benefit", "brand", "cta"],
            "readability_rules": {
                "min_contrast_ratio": 7.0 if billboard else 4.5,
                "distance_readability": "high" if billboard else "medium",
                "max_text_blocks": 3 if tiktok else 5,
                "safe_area": "center-left or top-third, avoid covering face/product",
            },
            "layout": "oversized stacked headline" if billboard or category in {"fmcg", "sports grooming"} else "minimal premium headline zone",
        }
