from __future__ import annotations

CATEGORY_PROFILES = {
    "beauty": {
        "emotion": ["softness", "confidence", "glow", "premium femininity"],
        "visuals": ["close-up skin texture", "serum hero", "warm champagne light"],
        "trust": ["natural skin texture", "clean background", "clinical but luxurious cues"],
    },
    "cosmetics": {
        "emotion": ["desire", "confidence", "editorial polish"],
        "visuals": ["product near face", "macro texture", "mirror reflections"],
        "trust": ["sharp product details", "realistic skin", "clean typography"],
    },
    "fmcg": {
        "emotion": ["freshness", "instant benefit", "daily trust"],
        "visuals": ["3/4 product packshot", "condensation", "high-contrast benefit cues"],
        "trust": ["readable label", "clean shelf presence", "benefit proof"],
    },
    "fashion": {
        "emotion": ["identity", "aspiration", "confidence"],
        "visuals": ["editorial pose", "fabric realism", "silhouette hierarchy"],
        "trust": ["premium material detail", "natural body proportions", "brand consistency"],
    },
    "wellness": {
        "emotion": ["calm", "balance", "comfort"],
        "visuals": ["warm neutrals", "soft light", "natural materials"],
        "trust": ["clean environment", "human warmth", "subtle proof cues"],
    },
    "sports grooming": {
        "emotion": ["cooling", "performance", "energy"],
        "visuals": ["blue energy", "airflow", "ice particles", "metallic gradients"],
        "trust": ["clinical freshness", "strong contrast", "readable benefit"],
    },
    "luxury branding": {
        "emotion": ["exclusivity", "status", "premium desire"],
        "visuals": ["black/gold", "negative space", "cinematic spotlight"],
        "trust": ["minimal typography", "expensive materials", "controlled reflections"],
    },
    "e-commerce": {
        "emotion": ["clarity", "confidence", "purchase readiness"],
        "visuals": ["product dominant", "benefit chips", "clean CTA"],
        "trust": ["label readability", "offer clarity", "review/proof space"],
    },
}


class CategoryCommercialEngine:
    def analyze(self, industry: str, product_type: str):
        key = industry.lower().strip()
        profile = CATEGORY_PROFILES.get(key, CATEGORY_PROFILES["e-commerce"])
        return {
            "category": key,
            "product_type": product_type,
            "emotion_targets": profile["emotion"],
            "visual_rules": profile["visuals"],
            "trust_rules": profile["trust"],
        }
