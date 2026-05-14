from __future__ import annotations

from typing import Any

# Permission contract for every known agent.
# Keys match the agent_name returned by each agent's run() result.
AGENT_PERMISSION_REGISTRY: dict[str, dict[str, Any]] = {
    "BusinessDiagnosisAgent": {
        "allowed_tools": ["recall_memory", "read_context_graph"],
        "allowed_memory_writes": ["short_term", "task"],
        "allowed_artifact_types": ["diagnosis"],
        "max_risk_level": "low",
    },
    "ImageDesignAgent": {
        "allowed_tools": ["recall_memory", "render_image"],
        "allowed_memory_writes": ["short_term", "task", "artifact"],
        "allowed_artifact_types": ["image_concept"],
        "max_risk_level": "medium",
    },
    "ImageQAAgent": {
        "allowed_tools": ["read_context_graph"],
        "allowed_memory_writes": ["short_term"],
        "allowed_artifact_types": ["qa_report"],
        "max_risk_level": "low",
    },
    "UpsellOpportunityAgent": {
        "allowed_tools": ["recall_memory"],
        "allowed_memory_writes": ["short_term", "task"],
        "allowed_artifact_types": ["upsell_analysis"],
        "max_risk_level": "low",
    },
    "VideoConceptAgent": {
        "allowed_tools": ["recall_memory", "render_video"],
        "allowed_memory_writes": ["short_term", "task", "artifact"],
        "allowed_artifact_types": ["video_concept"],
        "max_risk_level": "medium",
    },
    "StoryboardAgent": {
        "allowed_tools": ["recall_memory"],
        "allowed_memory_writes": ["short_term", "skill"],
        "allowed_artifact_types": ["storyboard"],
        "max_risk_level": "low",
    },
    "OfferAgent": {
        "allowed_tools": ["recall_memory"],
        "allowed_memory_writes": ["short_term", "task"],
        "allowed_artifact_types": ["offer_package"],
        "max_risk_level": "low",
    },
    # Workforce agents
    "IndustryIntelligenceAgent": {
        "allowed_tools": ["recall_memory", "read_context_graph"],
        "allowed_memory_writes": ["short_term", "task"],
        "allowed_artifact_types": ["industry_analysis"],
        "max_risk_level": "low",
    },
    "CreativeDirectorAgent": {
        "allowed_tools": ["recall_memory"],
        "allowed_memory_writes": ["short_term", "skill"],
        "allowed_artifact_types": ["creative_direction"],
        "max_risk_level": "low",
    },
    "VisualStrategistAgent": {
        "allowed_tools": ["recall_memory"],
        "allowed_memory_writes": ["short_term"],
        "allowed_artifact_types": ["visual_strategy"],
        "max_risk_level": "low",
    },
    "BrandConsistencyAgent": {
        "allowed_tools": ["read_context_graph"],
        "allowed_memory_writes": ["short_term"],
        "allowed_artifact_types": ["brand_report"],
        "max_risk_level": "low",
    },
    "CompositionAgent": {
        "allowed_tools": [],
        "allowed_memory_writes": ["short_term"],
        "allowed_artifact_types": ["composition_spec"],
        "max_risk_level": "low",
    },
    "TypographyAgent": {
        "allowed_tools": [],
        "allowed_memory_writes": ["short_term"],
        "allowed_artifact_types": ["typography_spec"],
        "max_risk_level": "low",
    },
    "ConversionOptimizationAgent": {
        "allowed_tools": ["recall_memory"],
        "allowed_memory_writes": ["short_term", "task"],
        "allowed_artifact_types": ["conversion_plan"],
        "max_risk_level": "medium",
    },
    "MotionThinkingAgent": {
        "allowed_tools": [],
        "allowed_memory_writes": ["short_term", "skill"],
        "allowed_artifact_types": ["motion_spec"],
        "max_risk_level": "low",
    },
    "DesignQAAgent": {
        "allowed_tools": ["read_context_graph"],
        "allowed_memory_writes": ["short_term"],
        "allowed_artifact_types": ["qa_report"],
        "max_risk_level": "low",
    },
    # Fallback for unknown agents
    "__default__": {
        "allowed_tools": [],
        "allowed_memory_writes": ["short_term"],
        "allowed_artifact_types": [],
        "max_risk_level": "low",
    },
}


def get_permissions(agent_name: str) -> dict[str, Any]:
    return AGENT_PERMISSION_REGISTRY.get(agent_name, AGENT_PERMISSION_REGISTRY["__default__"])
