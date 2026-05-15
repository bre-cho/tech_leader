class EnvironmentReactionEngine:
    def reason(self, sensory_effect: str | None, category: str) -> dict:
        effect = (sensory_effect or "premium glow").lower()
        if "cool" in effect or category in {"sports grooming", "fmcg"}:
            responses = {
                "hair":"subtle airflow direction",
                "mist":"moving from product toward face",
                "particles":"ice/crystal micro particles along motion path",
                "typography":"partially overlapped by airflow but still readable",
                "reflections":"cold blue-white highlights on pack edges",
            }
        elif category in {"beauty", "cosmetics", "wellness"}:
            responses = {
                "skin":"soft glow with controlled specular highlights",
                "particles":"subtle golden/petal particles behind subject",
                "background":"champagne gradient depth",
                "product":"warm rim light and clean reflection",
            }
        else:
            responses = {"background":"reacts to product color", "particles":"controlled depth accents", "lighting":"directional commercial highlights"}
        return {"effect": effect, "physics_responses": responses, "coherence_rules": ["one light direction", "effect must reinforce product benefit", "no random particles"]}
