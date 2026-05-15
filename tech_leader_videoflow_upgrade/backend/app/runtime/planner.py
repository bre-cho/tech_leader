from typing import Dict, Any, List

class TechnicalLeadPlanner:
    def plan(self, req: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "mission": "Build infrastructure-grade commercial creative workflow, not isolated generation.",
            "target_define": {
                "goal": req.get("goal", ""),
                "industry": req.get("industry", ""),
                "audience": req.get("audience", ""),
                "channel": req.get("channel", ""),
                "product": req.get("product", ""),
            },
            "research": {
                "category_assumptions": self._category_assumptions(req.get("industry", "")),
                "commercial_risks": ["low_attention", "weak_product_hero", "poor_typography", "no_memory_loop"]
            },
            "plan": [
                "build_context_graph",
                "run_commercial_reasoning",
                "compile_visual_prompt",
                "execute_provider_or_mock",
                "score_commercial_quality",
                "verify_operating_law",
                "promote_or_block",
                "update_memory_and_winner_dna"
            ],
            "required_agents": self._agents([]),
            "expected_outputs": [],
        }

    def _agents(self, outputs: List[str]) -> List[str]:
        agents = ["creative_director", "commercial_psychology", "attention_routing", "product_hero", "typography", "verification", "memory"]
        if "storyboard" in outputs or "video_concept" in outputs:
            agents += ["storyboard", "motion_language"]
        return agents

    def _category_assumptions(self, industry: str) -> Dict[str, str]:
        table = {
            "beauty": "skin trust, glow, natural texture, luxury softness",
            "cosmetics": "product texture, face-product connection, editorial beauty",
            "fmcg": "clear hero product, freshness cues, billboard readability",
            "fashion": "silhouette, fabric realism, confident pose, editorial lighting",
            "wellness": "calmness, trust, warmth, natural color harmony",
        }
        return {"category_logic": table.get(industry.lower(), "commercial clarity, trust, attention, conversion")}
