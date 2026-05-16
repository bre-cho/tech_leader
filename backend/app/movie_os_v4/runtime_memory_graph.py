from .schemas import MemoryGraphUpdate, MoodColorLensProfile, CharacterBible


class RuntimeMemoryGraph:
    def update(
        self,
        namespace: str,
        mood: MoodColorLensProfile,
        character: CharacterBible,
        provider: str,
    ) -> MemoryGraphUpdate:
        nodes = [
            {"id": f"{namespace}:mood:{mood.mood}", "type": "mood", "label": mood.mood},
            {"id": f"{namespace}:lens:{mood.lens}", "type": "lens", "label": mood.lens},
            {"id": f"{namespace}:character:{character.identity_lock}", "type": "character", "label": character.identity_lock},
            {"id": f"{namespace}:provider:{provider}", "type": "provider", "label": provider},
        ]

        edges = [
            {"source": nodes[0]["id"], "target": nodes[1]["id"], "relation": "uses_lens"},
            {"source": nodes[0]["id"], "target": nodes[2]["id"], "relation": "styles_character"},
            {"source": nodes[2]["id"], "target": nodes[3]["id"], "relation": "rendered_by"},
        ]

        winner_dna = {
            "mood": mood.mood,
            "lens": mood.lens,
            "lighting": mood.lighting,
            "character_identity": character.identity_lock,
            "provider": provider,
        }

        return MemoryGraphUpdate(
            namespace=namespace,
            nodes=nodes,
            edges=edges,
            winner_dna=winner_dna,
        )


runtime_memory_graph = RuntimeMemoryGraph()
