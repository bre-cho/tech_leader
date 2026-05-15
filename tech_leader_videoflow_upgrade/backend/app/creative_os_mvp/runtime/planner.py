from app.creative_os_mvp.models.schemas import CreativeRequest

class Planner:
    def plan(self, req: CreativeRequest) -> dict:
        brand = req.brand
        commercial_goal = brand.objective or "conversion"
        route = [
            "target_define", "commercial_research", "visual_plan", "commercial_reasoning",
            "prompt_compile", "render", "verify", "promotion_gate", "memory_update"
        ]
        return {
            "goal": f"Create {req.quality} commercial visual for {brand.product_name or brand.product_type}",
            "commercial_goal": commercial_goal,
            "category": brand.industry,
            "workflow_route": route,
            "output_targets": req.output_targets,
            "risks": ["text readability", "product distortion", "weak CTA", "brand mismatch"],
        }
