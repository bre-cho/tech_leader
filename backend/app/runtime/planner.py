class Planner:
    def create_plan(self, request):
        return {
            "workflow": "design-to-video",
            "goal": "Generate revenue loop from static design to video upsell",
            "steps": [
                {"step": "target_define", "output": "business objective and constraints"},
                {"step": "research", "output": "industry playbook and recalled winner DNA"},
                {"step": "plan", "output": "agent execution plan"},
                {"step": "execute", "output": "design concepts, scores, upsell, storyboard, offers"},
                {"step": "verify", "output": "quality and governance checks"},
                {"step": "distill_to_skill", "output": "reusable skill pattern"},
                {"step": "memory_update", "output": "context graph and winner DNA"},
            ],
        }
