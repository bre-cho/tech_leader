from app.creative_infra_mvp.contracts import BusinessInput, AgentResult

class CreativeDirectorAgent:
    def run(self, business: BusinessInput):
        direction = f"{business.brand_name} should communicate {business.goal} through a category-specific commercial visual system."
        return AgentResult(agent="CreativeDirectorAgent", status="completed", output={"creative_direction": direction})

class VisualStrategistAgent:
    def run(self, business: BusinessInput):
        return AgentResult(agent="VisualStrategistAgent", status="completed", output={
            "hook": f"Show the strongest outcome of {business.product_name} in the first visual beat",
            "attention_strategy": "face/product first, benefit second, CTA last",
            "trust_strategy": "real texture, clean lighting, readable product, no fake over-processing"
        })

class CompositionAgent:
    def run(self, regions):
        return AgentResult(agent="CompositionAgent", status="completed", output={
            "layout_regions": [r.model_dump() for r in regions],
            "balance_rule": "product and emotional anchor must not compete; route eye movement intentionally"
        })

class TypographyAgent:
    def run(self, ds):
        return AgentResult(agent="TypographyAgent", status="completed", output={
            "typography": ds.typography,
            "readability": "headline readable for mobile and billboard, CTA clear in lower third"
        })

class BrandConsistencyAgent:
    def run(self, ds):
        return AgentResult(agent="BrandConsistencyAgent", status="completed", output={
            "colors": ds.colors,
            "visual_language": ds.visual_language,
            "consistency_rule": "all outputs must preserve brand color, tone, material, and spacing DNA"
        })

class ConversionOptimizationAgent:
    def run(self, business):
        return AgentResult(agent="ConversionOptimizationAgent", status="completed", output={
            "cta": business.offer or "Discover the result today",
            "conversion_logic": "show outcome + product proof + low-friction CTA"
        })

class MotionThinkingAgent:
    def run(self, business):
        return AgentResult(agent="MotionThinkingAgent", status="completed", output={
            "poster_to_video": [
                "Scene 1: hook close-up",
                "Scene 2: product moves into frame, gaze follows product",
                "Scene 3: benefit proof and texture detail",
                "Scene 4: CTA end card"
            ]
        })

class IndustryIntelligenceAgent:
    def run(self, business):
        return AgentResult(agent="IndustryIntelligenceAgent", status="completed", output={
            "industry": business.industry,
            "adaptation": "apply category-specific perception, material, lighting and conversion rules"
        })

class DesignQAAgent:
    def run(self):
        return AgentResult(agent="DesignQAAgent", status="completed", output={
            "qa_rules": ["trust", "readability", "emotional impact", "visual balance", "conversion"]
        })
