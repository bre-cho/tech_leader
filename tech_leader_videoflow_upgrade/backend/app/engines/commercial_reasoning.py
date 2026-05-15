from typing import Dict, Any, List

class AttentionRoutingEngine:
    def analyze(self, req: Dict[str, Any]) -> Dict[str, Any]:
        category = req["industry"].lower()
        if category in ["beauty", "cosmetics"]:
            route = ["face/eyes", "skin glow", "product hero", "headline", "CTA"]
        elif category in ["fmcg", "sports grooming"]:
            route = ["headline", "cooling/product effect", "product hero", "benefit proof", "CTA"]
        else:
            route = ["hero visual", "headline", "product/service proof", "CTA"]
        return {
            "visual_attention_order": route,
            "dopamine_points": ["strong contrast", "motion cue", "human face", "premium texture"],
            "retention_points": ["eye contact", "product detail", "benefit proof"],
            "conversion_points": ["CTA clarity", "offer visibility", "trust signal"],
            "attention_score": min(96, 72 + len(route)*4)
        }

class TypographyHierarchyEngine:
    def analyze(self, req: Dict[str, Any]) -> Dict[str, Any]:
        platform = req.get("platform", "")
        billboard = "billboard" in platform or "outdoor" in platform
        return {
            "font_logic": "bold condensed sans-serif for FMCG/performance, elegant serif for luxury beauty",
            "hierarchy": ["headline", "benefit", "CTA", "legal/minor text"],
            "readability_rules": {
                "max_words_headline": 5 if billboard else 8,
                "high_contrast": True,
                "safe_text_zone": True,
                "distance_readability": billboard
            },
            "typography_score": 88 if billboard else 84
        }

class ProductHeroEngine:
    def analyze(self, req: Dict[str, Any]) -> Dict[str, Any]:
        product = req["product_or_service"].lower()
        if any(x in product for x in ["serum", "perfume", "bottle", "cosmetic", "skincare"]):
            angle = "premium 3/4 hero angle with glass reflections and liquid clarity"
            material = ["glass", "liquid", "metal cap", "soft reflection"]
        elif any(x in product for x in ["drink", "shampoo", "fmcg"]):
            angle = "bold front 3/4 packshot with condensation and strong benefit visibility"
            material = ["plastic/glass packaging", "condensation", "water droplets"]
        else:
            angle = "clear hero perspective with product recognizable at thumbnail distance"
            material = ["clean edges", "realistic reflections"]
        return {"hero_angle": angle, "material_logic": material, "product_clarity_score": 90}

class EnvironmentReactionEngine:
    def analyze(self, req: Dict[str, Any]) -> Dict[str, Any]:
        industry = req["industry"].lower()
        if "sports" in industry or "fmcg" in industry:
            reactions = ["mist trails", "cool airflow", "particle movement", "hair/fabric slight motion"]
        elif industry in ["beauty", "cosmetics"]:
            reactions = ["gold particles", "soft glow", "skin highlight response", "floating botanical elements"]
        else:
            reactions = ["depth haze", "lighting gradients", "subtle atmospheric particles"]
        return {"environment_reactions": reactions, "physics_consistency_required": True, "reaction_score": 86}

class CommercialPsychologyEngine:
    def analyze(self, req: Dict[str, Any]) -> Dict[str, Any]:
        industry = req["industry"].lower()
        mapping = {
            "beauty": {"emotion": "soft confidence", "perception": "premium glow", "buying_trigger": "self-improvement"},
            "cosmetics": {"emotion": "desire", "perception": "editorial beauty", "buying_trigger": "transformation"},
            "fmcg": {"emotion": "freshness", "perception": "performance trust", "buying_trigger": "instant benefit"},
            "fashion": {"emotion": "confidence", "perception": "status/elegance", "buying_trigger": "identity upgrade"},
            "wellness": {"emotion": "calm", "perception": "trust and safety", "buying_trigger": "relief"}
        }
        return mapping.get(industry, {"emotion": "trust", "perception": "commercial clarity", "buying_trigger": "problem solution"})

class BillboardPrintEngine:
    def analyze(self, req: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "exports": ["social_preview", "4k_web", "8k_print"],
            "print_rules": {
                "cmyk_safe_palette": True,
                "large_format_contrast": True,
                "no_small_critical_text": True,
                "upscale_integrity": True
            },
            "print_score": 87
        }

class CategoryCommercialEngine:
    def analyze(self, req: Dict[str, Any]) -> Dict[str, Any]:
        category = req["industry"].lower()
        presets = {
            "beauty": ["skin texture realism", "warm luxury glow", "face-product connection"],
            "cosmetics": ["color payoff", "editorial close-up", "product texture"],
            "fmcg": ["benefit-first headline", "packshot clarity", "freshness cues"],
            "fashion": ["fabric realism", "silhouette", "confident pose"],
            "wellness": ["soft natural palette", "trust cues", "calm composition"],
        }
        return {"category_rules": presets.get(category, ["clear commercial promise", "trust signal", "CTA"]), "category_fit_score": 89}

class CommercialVisualReasoningEngine:
    def __init__(self):
        self.attention = AttentionRoutingEngine()
        self.typography = TypographyHierarchyEngine()
        self.product = ProductHeroEngine()
        self.environment = EnvironmentReactionEngine()
        self.psychology = CommercialPsychologyEngine()
        self.print_engine = BillboardPrintEngine()
        self.category = CategoryCommercialEngine()

    def reason(self, req: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "attention": self.attention.analyze(req),
            "typography": self.typography.analyze(req),
            "product_hero": self.product.analyze(req),
            "environment": self.environment.analyze(req),
            "psychology": self.psychology.analyze(req),
            "print": self.print_engine.analyze(req),
            "category": self.category.analyze(req),
        }
        scores = [
            result["attention"]["attention_score"],
            result["typography"]["typography_score"],
            result["product_hero"]["product_clarity_score"],
            result["environment"]["reaction_score"],
            result["print"]["print_score"],
            result["category"]["category_fit_score"],
        ]
        result["commercial_reasoning_score"] = round(sum(scores)/len(scores), 2)
        return result
