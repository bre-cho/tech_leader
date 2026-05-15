REQUIRED_STAGES = [
    "WORKSPACE",
    "WORKFLOWS",
    "AI_WORKFORCE",
    "MEMORY_RECALL",
    "CREATIVE_GRAPH_REASONING",
    "VARIANT_GENERATION",
    "SCORING",
    "OPTIMIZATION",
    "MEMORY_UPDATE",
    "WINNER_DNA"
]

class OperatingLaw:
    def validate(self, stages):
        missing = [s for s in REQUIRED_STAGES if s not in stages]
        if missing:
            raise ValueError("Blocked by AI-Native Business OS Law. Missing: " + ", ".join(missing))
        return True
