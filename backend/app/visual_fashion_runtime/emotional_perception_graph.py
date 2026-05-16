from .schemas import EmotionalPerceptionGraph, VisualDNA


class EmotionalPerceptionGraphBuilder:
    def build(self, dna: VisualDNA) -> EmotionalPerceptionGraph:
        if "pastel" in dna.archetype:
            nodes = [
                {"id": "playful_luxury", "type": "emotion", "label": "Playful luxury"},
                {"id": "youth_desire", "type": "commerce", "label": "Youthful aspiration"},
                {"id": "motion_energy", "type": "motion", "label": "Kinetic fashion energy"},
                {"id": "identity_fantasy", "type": "psychology", "label": "I want to become her"},
            ]
            dominant = "playful luxury confidence"
            hook = "pastel motion + low-angle fashion dominance + soft feminine eye contact"
        else:
            nodes = [
                {"id": "quiet_luxury", "type": "emotion", "label": "Quiet luxury"},
                {"id": "soft_intimacy", "type": "beauty", "label": "Soft intimacy"},
                {"id": "premium_trust", "type": "commerce", "label": "Premium trust"},
                {"id": "feminine_refinement", "type": "psychology", "label": "Feminine refinement"},
            ]
            dominant = "soft luxury intimacy"
            hook = "pearl detail + glossy hair + quiet luxury flatlay"

        edges = [
            {"source": nodes[0]["id"], "target": nodes[1]["id"], "relation": "amplifies"},
            {"source": nodes[1]["id"], "target": nodes[2]["id"], "relation": "supports"},
            {"source": nodes[2]["id"], "target": nodes[3]["id"], "relation": "converts"},
        ]

        return EmotionalPerceptionGraph(
            nodes=nodes,
            edges=edges,
            dominant_emotion=dominant,
            virality_hook=hook,
        )


emotional_perception_graph_builder = EmotionalPerceptionGraphBuilder()
