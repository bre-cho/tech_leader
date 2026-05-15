class CapabilityRouter:
    def route(self, plan: dict) -> dict:
        category = (plan.get("category") or "").lower()
        agents = ["commercial_intelligence", "prompt_compiler", "visual_renderer", "qa", "memory"]
        if category in {"beauty", "cosmetics", "fashion", "wellness"}:
            agents += ["beauty_perception", "color_intelligence"]
        if category in {"fmcg", "sports grooming", "food & beverage"}:
            agents += ["product_hero", "environment_reaction"]
        return {"agents": agents, "provider_strategy": "fast_explore_then_premium_render"}
