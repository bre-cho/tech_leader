class TypographyHierarchyEngine:
    def reason(self, category: str, channel: str, objective: str) -> dict:
        channel = channel.lower()
        billboard = any(x in channel for x in ["billboard", "outdoor", "mall", "led"])
        tiktok = "tiktok" in channel or "reel" in channel
        if billboard:
            headline = {"font_style":"ultra-bold condensed sans-serif", "size":"oversized", "tracking":"tight", "contrast":"very high"}
            min_readability = 0.9
        elif tiktok:
            headline = {"font_style":"bold geometric sans-serif", "size":"large stacked", "tracking":"normal-tight", "contrast":"high"}
            min_readability = 0.82
        elif category in {"beauty","cosmetics","luxury branding"}:
            headline = {"font_style":"elegant serif + clean sans", "size":"medium-large", "tracking":"premium airy", "contrast":"soft high"}
            min_readability = 0.78
        else:
            headline = {"font_style":"bold commercial sans", "size":"large", "tracking":"normal", "contrast":"high"}
            min_readability = 0.8
        return {
            "headline_system": headline,
            "hierarchy": ["headline", "sub-benefit", "product name", "CTA"],
            "safe_text_zones": ["top third", "right negative space", "bottom CTA band"],
            "billboard_distance_readability": min_readability,
            "rules": ["max 7 headline words", "avoid thin font on bright background", "reserve clean typography area"],
        }
