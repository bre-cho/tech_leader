from __future__ import annotations


class EnvironmentReactionEngine:
    def plan(self, category: str, emotion_targets):
        if category in {"fmcg", "sports grooming"} or "freshness" in emotion_targets:
            return {
                "reaction_type": "cooling airflow",
                "affected_elements": ["hair", "mist", "particles", "typography edges", "reflections"],
                "physics_rules": [
                    "airflow direction must match product benefit",
                    "particles move away from product source",
                    "typography may be partially overlapped but remains readable",
                ],
            }
        if category in {"beauty", "cosmetics"}:
            return {
                "reaction_type": "soft glow and cosmetic particles",
                "affected_elements": ["skin highlights", "serum glow", "gold particles", "background bokeh"],
                "physics_rules": [
                    "particles should enhance depth, not clutter",
                    "skin texture must remain visible",
                    "product reflection must match key light",
                ],
            }
        return {
            "reaction_type": "brand atmosphere",
            "affected_elements": ["background", "light", "surface reflections"],
            "physics_rules": ["environment supports product category", "no random effects"],
        }
