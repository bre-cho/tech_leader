from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class DesignBusinessInput:
    founder_name: str = "TungNS"
    brand_name: str = "AI Design Workforce OS"
    niche: str = "thiết kế AI cho poster/banner/thumbnail quảng cáo"
    target_audience: str = "chủ shop, creator, marketer và SME"
    core_promise: str = "tạo visual quảng cáo chuẩn agency bằng AI và biến thành doanh thu"
    product_category: str = "poster, banner, thumbnail, prompt/template pack"
    primary_platform: str = "TikTok"
    visual_style: str = "Luxury editorial, product-first, high-conversion advertising"
    monthly_revenue_goal: str = "tăng trưởng từ sản phẩm số + dịch vụ setup"


def _payload(payload: dict[str, Any] | None) -> DesignBusinessInput:
    payload = payload or {}
    allowed = {field.name for field in DesignBusinessInput.__dataclass_fields__.values()}
    return DesignBusinessInput(**{k: v for k, v in payload.items() if k in allowed})


def run_brand_brain(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = _payload(payload)
    brand_id = data.brand_name.lower().replace(" ", "-")
    employees = [
        {"id": "brand-strategy-agent", "name": "Brand Strategy Agent", "mission": "Định vị thương hiệu, content pillars và product ladder", "kpi": "Brand clarity >= 90"},
        {"id": "design-research-agent", "name": "Design Research Agent", "mission": "Quét trend, đối thủ, visual gap", "kpi": "Trend-to-content fit >= 85"},
        {"id": "poster-director-agent", "name": "Poster Director Agent", "mission": "Tạo poster prompt, layout, lighting, typography", "kpi": "Poster score >= 88"},
        {"id": "content-agent", "name": "Content Agent", "mission": "Tạo short script, caption, carousel, email", "kpi": "Hook score >= 90"},
        {"id": "offer-agent", "name": "Offer Agent", "mission": "Đóng gói prompt pack, template pack, course, service", "kpi": "Offer clarity >= 90"},
        {"id": "analytics-agent", "name": "Analytics Agent", "mission": "Đọc data, cập nhật Winner DNA, đề xuất clone/kill/improve", "kpi": "Every campaign has a decision"},
    ]
    graph = {
        "entities": [
            {"id": f"{brand_id}:brand", "type": "brand", "name": data.brand_name, "summary": f"Thương hiệu cá nhân giúp {data.target_audience} dùng AI để thiết kế và bán hàng."},
            {"id": f"{brand_id}:audience", "type": "audience", "name": data.target_audience, "summary": "Khách hàng cần thiết kế nhanh, đẹp, có chuyển đổi, không phụ thuộc agency."},
            {"id": f"{brand_id}:style", "type": "style", "name": data.visual_style, "summary": "Style DNA giữ nhất quán poster, banner, thumbnail và landing visual."},
            {"id": f"{brand_id}:offer", "type": "offer", "name": data.product_category, "summary": data.core_promise},
            {"id": f"{brand_id}:metric", "type": "metric", "name": "Revenue Intelligence", "summary": data.monthly_revenue_goal},
        ],
        "relations": [
            {"from": f"{brand_id}:brand", "to": f"{brand_id}:audience", "relation": "serves", "weight": 0.96},
            {"from": f"{brand_id}:style", "to": f"{brand_id}:offer", "relation": "increases_perceived_value", "weight": 0.88},
            {"from": f"{brand_id}:metric", "to": f"{brand_id}:style", "relation": "updates_winner_memory", "weight": 0.9},
        ],
    }
    return {
        "input": asdict(data),
        "positioning": f"{data.brand_name} giúp {data.target_audience} dùng AI tạo thiết kế quảng cáo có khả năng bán hàng và đóng gói thành sản phẩm số/doanh thu tự động.",
        "system_formula": ["DATA", "DESIGN_CONTEXT_GRAPH", "BRAND_BRAIN", "AI_DESIGN_EMPLOYEES", "WORKFLOWS", "AUTOMATION", "ANALYTICS", "OPTIMIZATION", "WINNER_DNA", "SCALE"],
        "context_graph": graph,
        "ai_employees": employees,
        "workflows": [
            {
                "id": "daily-content-to-lead",
                "name": "Daily Content to Lead",
                "steps": ["trend_scan", "poster_demo", "short_script", "lead_magnet", "analytics_decision", "winner_memory_update"],
            },
            {
                "id": "winner-to-product",
                "name": "Winner to Digital Product",
                "steps": ["package_prompt_pack", "landing_copy", "email_nurture", "checkout", "clone_winner"],
            },
        ],
        "quality_gates": ["NO BRAND DNA -> NO CONTENT", "NO PRODUCT FOCUS -> NO POSTER", "NO REVENUE SIGNAL -> NO CLONE", "NO WINNER MEMORY -> NO NEXT PRODUCT"],
    }
