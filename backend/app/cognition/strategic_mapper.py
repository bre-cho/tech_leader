from __future__ import annotations

from typing import Any


_BUSINESS_GOAL_MAP = {
    "ecommerce": {"goal": "increase_revenue", "kpi": "conversion_rate", "channel": "social"},
    "fashion": {"goal": "brand_awareness", "kpi": "engagement_rate", "channel": "instagram"},
    "food": {"goal": "retention", "kpi": "repeat_order_rate", "channel": "tiktok"},
    "beauty": {"goal": "upsell", "kpi": "aov", "channel": "youtube"},
    "saas": {"goal": "lead_generation", "kpi": "cpl", "channel": "linkedin"},
    "education": {"goal": "enrollment", "kpi": "signup_rate", "channel": "search"},
}

_RISK_IMPACT_MAP = {
    "increase_revenue": {"revenue_impact": "high", "cost_impact": "medium", "risk": "low"},
    "brand_awareness": {"revenue_impact": "medium", "cost_impact": "high", "risk": "medium"},
    "retention": {"revenue_impact": "medium", "cost_impact": "low", "risk": "low"},
    "upsell": {"revenue_impact": "high", "cost_impact": "low", "risk": "low"},
    "lead_generation": {"revenue_impact": "medium", "cost_impact": "medium", "risk": "medium"},
    "enrollment": {"revenue_impact": "medium", "cost_impact": "medium", "risk": "low"},
}


class StrategicObjectiveMapper:
    """
    Maps a task/workflow to a business goal → revenue/cost/risk impact model.
    Used by the economic cognition layer and economic audit.
    """

    def map(self, industry: str, task_description: str = "") -> dict[str, Any]:
        industry_key = industry.lower().strip()
        goal_meta = _BUSINESS_GOAL_MAP.get(industry_key, {
            "goal": "growth", "kpi": "conversion_rate", "channel": "social"
        })
        impact = _RISK_IMPACT_MAP.get(goal_meta["goal"], {
            "revenue_impact": "unknown", "cost_impact": "unknown", "risk": "unknown"
        })
        return {
            "industry": industry,
            "mapped_business_goal": goal_meta["goal"],
            "primary_kpi": goal_meta["kpi"],
            "recommended_channel": goal_meta["channel"],
            "revenue_impact": impact["revenue_impact"],
            "cost_impact": impact["cost_impact"],
            "risk_level": impact["risk"],
            "task_description": task_description,
        }

    def is_mapped(self, industry: str) -> bool:
        return industry.lower().strip() in _BUSINESS_GOAL_MAP
