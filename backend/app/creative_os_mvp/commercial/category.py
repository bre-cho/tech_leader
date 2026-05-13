class CategoryCommercialEngine:
    def reason(self, category: str, product_type: str) -> dict:
        c = category.lower()
        presets = {
            "beauty": {"visual_dna":["glowing skin", "serum foreground", "warm champagne light"], "avoid":["plastic skin", "over-smoothed face"]},
            "cosmetics": {"visual_dna":["lip/eye macro", "color payoff", "editorial beauty contrast"], "avoid":["muddy makeup", "wrong shade"]},
            "fmcg": {"visual_dna":["bold headline", "packshot clarity", "sensory effect"], "avoid":["small product", "weak label"]},
            "sports grooming": {"visual_dna":["cooling motion", "blue energy", "clean skin/scalp signal"], "avoid":["warm spa mood", "soft weak contrast"]},
            "fashion": {"visual_dna":["silhouette", "fabric realism", "editorial pose"], "avoid":["fake fabric", "stiff posture"]},
            "wellness": {"visual_dna":["natural softness", "botanical cues", "clean trust"], "avoid":["medical fear", "oversaturated greens"]},
        }
        result = presets.get(c, {"visual_dna":["clear hero", "benefit cue", "clean composition"], "avoid":["unclear hierarchy"]})
        result.update({"category": category, "product_type": product_type})
        return result
