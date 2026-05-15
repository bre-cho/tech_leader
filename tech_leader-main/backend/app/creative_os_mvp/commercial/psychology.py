class CommercialPsychologyEngine:
    CATEGORY_MAP = {
        "sports grooming": {"emotion":"cold freshness", "perception":"performance confidence", "buying_trigger":"instant clean feeling"},
        "fmcg": {"emotion":"sensory clarity", "perception":"daily utility + trust", "buying_trigger":"recognizable benefit"},
        "beauty": {"emotion":"soft confidence", "perception":"premium skin and trust", "buying_trigger":"visible transformation"},
        "cosmetics": {"emotion":"desire + self-expression", "perception":"beauty authority", "buying_trigger":"color payoff / glow"},
        "fashion": {"emotion":"confidence", "perception":"style identity", "buying_trigger":"aspirational silhouette"},
        "wellness": {"emotion":"calm safety", "perception":"natural care", "buying_trigger":"comfort and relief"},
    }
    def reason(self, category: str, objective: str) -> dict:
        base = self.CATEGORY_MAP.get(category.lower(), {"emotion":"trust", "perception":"clear value", "buying_trigger":"credible outcome"})
        graph = [
            {"source": base["emotion"], "relation":"creates", "target":base["perception"], "weight":.84},
            {"source":base["perception"], "relation":"supports", "target":objective or "conversion", "weight":.79},
        ]
        return {"category_psychology": base, "perception_graph": graph, "trust_signals":["real texture", "controlled lighting", "specific benefit cue", "readable product"]}
