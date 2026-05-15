from __future__ import annotations


class ProductHeroEngine:
    def plan(self, product_type: str, category: str):
        pt = product_type.lower()
        if any(x in pt for x in ["serum", "perfume", "bottle", "cosmetic"]):
            return {
                "angle": "perfect 3/4 hero perspective",
                "lighting": "premium rim light with controlled glass reflections",
                "material_rules": ["glass refraction", "liquid depth", "metallic cap highlights"],
                "placement": "foreground dominant, aligned with face or benefit cue",
            }
        if any(x in pt for x in ["drink", "shampoo", "fmcg"]):
            return {
                "angle": "large front 3/4 packshot",
                "lighting": "high contrast commercial reflection",
                "material_rules": ["condensation", "label readability", "cold highlight"],
                "placement": "hero center-right with headline wrapping around motion",
            }
        return {
            "angle": "clean commercial hero angle",
            "lighting": "softbox commercial lighting",
            "material_rules": ["sharp edges", "label readability", "real scale"],
            "placement": "foreground product hero with negative space for CTA",
        }
