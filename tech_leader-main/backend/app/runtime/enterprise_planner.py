from __future__ import annotations

from app.core.contracts import BusinessInput


class Planner:
    def plan(self, business: BusinessInput):
        return {
            "workflow": "commercial_creative_campaign",
            "objective": business.goal.value,
            "steps": [
                "define business context",
                "reason commercial visual logic",
                "compile premium rendering prompt",
                "execute provider",
                "verify commercial quality",
                "promote if score passes",
                "save memory and winner dna",
            ],
        }
