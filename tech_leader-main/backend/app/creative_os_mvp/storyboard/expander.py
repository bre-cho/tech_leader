class StoryboardExpander:
    def expand(self, req, reasoning) -> list[dict]:
        product=req.brand.product_name or req.brand.product_type or "product"
        return [
            {"scene":1, "role":"hook", "visual": reasoning.attention_route[0]["element"] if reasoning.attention_route else "hero visual", "duration":"2s"},
            {"scene":2, "role":"product reveal", "visual": f"3/4 hero reveal of {product}", "duration":"3s"},
            {"scene":3, "role":"benefit proof", "visual": reasoning.environment_reaction.get("effect"), "duration":"4s"},
            {"scene":4, "role":"trust", "visual": reasoning.psychology.get("category_psychology",{}).get("perception"), "duration":"3s"},
            {"scene":5, "role":"CTA", "visual":"clean typography CTA end card", "duration":"3s"},
        ]
