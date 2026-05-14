from __future__ import annotations

from typing import Any

# Required contracts every agent must satisfy in the workforce registry
REQUIRED_AGENT_CONTRACTS = [
    "role",
    "input_schema",
    "output_schema",
    "handoff_contract",
    "escalation_contract",
]


class WorkforceAuditor:
    """
    Audits the multi-agent workforce registry to ensure every agent
    declares the required contracts.
    """

    def __init__(self):
        self._registry = self._build_registry()

    def run(self) -> dict[str, Any]:
        gaps: list[dict] = []
        complete = 0

        for agent_name, contract in self._registry.items():
            missing = [f for f in REQUIRED_AGENT_CONTRACTS if not contract.get(f)]
            if missing:
                gaps.append({"agent_name": agent_name, "missing_contracts": missing})
            else:
                complete += 1

        status = "PASS" if not gaps else "WARN"

        return {
            "workforce_status": status,
            "total_agents": len(self._registry),
            "agents_with_full_contract": complete,
            "agents_with_gaps": gaps,
            "required_contracts": REQUIRED_AGENT_CONTRACTS,
        }

    def _build_registry(self) -> dict[str, dict[str, Any]]:
        # Introspect known workforce agents.  In production this would be auto-
        # discovered via agent metadata; here we build it from the known roster.
        from app.workforce.agents.creative_director import CreativeDirectorAgent
        from app.workforce.agents.visual_strategist import VisualStrategistAgent
        from app.workforce.agents.composition import CompositionAgent
        from app.workforce.agents.typography import TypographyAgent
        from app.workforce.agents.brand_consistency import BrandConsistencyAgent
        from app.workforce.agents.conversion import ConversionOptimizationAgent
        from app.workforce.agents.motion import MotionThinkingAgent
        from app.workforce.agents.industry import IndustryIntelligenceAgent
        from app.workforce.agents.design_qa import DesignQAAgent

        agents = [
            IndustryIntelligenceAgent(),
            CreativeDirectorAgent(),
            VisualStrategistAgent(),
            BrandConsistencyAgent(),
            CompositionAgent(),
            TypographyAgent(),
            ConversionOptimizationAgent(),
            MotionThinkingAgent(),
            DesignQAAgent(),
        ]

        registry: dict[str, dict[str, Any]] = {}
        for agent in agents:
            name = getattr(agent, "agent_name", type(agent).__name__)
            registry[name] = {
                "role": getattr(agent, "role", None),
                "input_schema": getattr(agent, "input_schema", None),
                "output_schema": getattr(agent, "output_schema", None),
                "handoff_contract": getattr(agent, "handoff_contract", None),
                "escalation_contract": getattr(agent, "escalation_contract", None),
            }
        return registry
