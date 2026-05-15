from app.creative_infra_mvp.contracts import VerificationReport, DesignSystem, CanvasRegion, GraphEdge

class VerificationEngine:
    def verify(self, ds: DesignSystem, regions: list[CanvasRegion], edges: list[GraphEdge], prompt: str):
        checks = {
            "design_system_extracted": bool(ds.colors and ds.typography and ds.visual_language),
            "canvas_has_product_region": any(r.name == "product_hero" for r in regions),
            "canvas_has_cta_region": any(r.name == "cta_zone" for r in regions),
            "creative_graph_exists": len(edges) >= 4,
            "prompt_has_business_context": "Brand:" in prompt and "Goal:" in prompt,
            "prompt_has_canvas_logic": "AI-NATIVE DESIGN CANVAS" in prompt,
            "prompt_has_graph_logic": "CREATIVE INTELLIGENCE GRAPH" in prompt,
            "prompt_has_motion_logic": "POSTER-TO-VIDEO LOGIC" in prompt,
        }
        score = round(sum(checks.values()) / len(checks) * 100, 2)
        return VerificationReport(
            passed=score >= 90,
            score=score,
            checks=checks,
            issues=[k for k, v in checks.items() if not v]
        )
