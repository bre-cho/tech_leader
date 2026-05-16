from .schemas import NarrativeGraph, NarrativeNode


class CreativeAbstractionLayer:
    def build_narrative_graph(self, prompt: str) -> NarrativeGraph:
        nodes = [
            NarrativeNode(label="Director Prompt", role="input", description=prompt, weight=1.0),
            NarrativeNode(label="Hero Identity", role="character", description="Define the central cinematic figure and identity lock.", weight=0.98),
            NarrativeNode(label="World Mood", role="mood", description="Define the world, atmosphere, genre, and visual rules.", weight=0.94),
            NarrativeNode(label="Transformation Arc", role="story", description="Move from reveal to escalation to payoff.", weight=0.9),
            NarrativeNode(label="Emotional Peak", role="rhythm", description="Identify the highest emotional and visual energy moment.", weight=0.88),
            NarrativeNode(label="Final Assembly", role="delivery", description="Build final movie timeline, tracks, and artifacts.", weight=0.86),
        ]

        edges = [
            {"source": nodes[0].id, "target": nodes[1].id, "relation": "defines"},
            {"source": nodes[1].id, "target": nodes[2].id, "relation": "inhabits"},
            {"source": nodes[2].id, "target": nodes[3].id, "relation": "enables"},
            {"source": nodes[3].id, "target": nodes[4].id, "relation": "peaks_at"},
            {"source": nodes[4].id, "target": nodes[5].id, "relation": "resolves_into"},
        ]

        return NarrativeGraph(nodes=nodes, edges=edges)


creative_abstraction_layer = CreativeAbstractionLayer()
