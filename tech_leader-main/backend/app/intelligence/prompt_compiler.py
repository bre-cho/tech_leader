from __future__ import annotations

from app.core.contracts import BusinessInput, VisualDecision


class CommercialPromptCompiler:
    def compile(self, business: BusinessInput, decision: VisualDecision):
        prompt = f'''
Premium commercial advertising visual for {business.brand_name}, product: {business.product_name}.
Category: {business.industry}. Product type: {business.product_type}.
Audience: {business.target_audience}. Campaign goal: {business.goal.value}.

COMMERCIAL VISUAL REASONING:
Attention routing order: {' → '.join(decision.attention_route)}.
The composition must guide the viewer eye from the first focal point to product desire, trust proof, and CTA readiness.

TYPOGRAPHY INTELLIGENCE:
Use {decision.typography_plan['headline_style']}.
Layout rule: {decision.typography_plan['layout']}.
Keep a clean typography-safe area. Make headline readable at social and billboard distance.

PRODUCT HERO ENGINE:
Product angle: {decision.product_hero_plan['angle']}.
Lighting: {decision.product_hero_plan['lighting']}.
Material rules: {', '.join(decision.product_hero_plan['material_rules'])}.
Placement: {decision.product_hero_plan['placement']}.

ENVIRONMENT REACTION:
Reaction type: {decision.environment_reaction_plan['reaction_type']}.
Affected elements: {', '.join(decision.environment_reaction_plan['affected_elements'])}.
Physics rules: {', '.join(decision.environment_reaction_plan['physics_rules'])}.

COMMERCIAL PSYCHOLOGY:
Map visual cues to buying psychology: {decision.commercial_psychology}.

STYLE:
Ultra realistic, commercial photography, cinematic lighting, premium texture fidelity,
high trust brand aesthetic, clean composition, no watermark, no distorted text,
8K master quality, print-ready sharpness.
'''
        negative = (
            "distorted logo, unreadable text, broken hands, deformed product, wrong label, "
            "plastic skin, over-smoothing, low resolution, cluttered layout, random effects, "
            "bad anatomy, duplicate product, cropped CTA, fake reflections"
        )
        return prompt.strip(), negative
