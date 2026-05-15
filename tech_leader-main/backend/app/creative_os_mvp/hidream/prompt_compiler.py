from app.creative_os_mvp.models.schemas import CreativeRequest, CommercialReasoning

class HiDreamCommercialPromptCompiler:
    def compile(self, req: CreativeRequest, reasoning: CommercialReasoning) -> tuple[str,str]:
        b=req.brand
        cat=reasoning.category
        attention=" → ".join([x["element"] for x in reasoning.attention_route])
        prompt = f"""
Premium commercial advertising visual for {b.brand_name or 'a premium brand'}, product: {b.product_name or b.product_type}.
Industry/category: {b.industry}. Objective: {b.objective}. Audience: {b.audience}.
Commercial visual reasoning: guide viewer attention in this order: {attention}.
Category visual DNA: {', '.join(cat.get('visual_dna', []))}.
Product hero: {reasoning.product_hero.get('hero_angle')}, placement {reasoning.product_hero.get('placement')}, material cues {', '.join(reasoning.product_hero.get('material_cues', []))}.
Typography system: {reasoning.typography.get('headline_system')}; reserve clean readable typography zones: {', '.join(reasoning.typography.get('safe_text_zones', []))}.
Environment reaction: {reasoning.environment_reaction.get('effect')} with coherent physics responses {reasoning.environment_reaction.get('physics_responses')}.
Psychology: create {reasoning.psychology.get('category_psychology',{}).get('emotion')} leading to {reasoning.psychology.get('category_psychology',{}).get('perception')}.
Style: cinematic commercial photography, realistic texture fidelity, premium material realism, controlled depth of field, professional ad composition, 8K ultra high resolution.
Aspect ratio {req.aspect_ratio}. Keep product readable and composition conversion-focused.
Brief: {req.brief}
""".strip()
        negative = "distorted hands, warped product, unreadable logo, broken typography, plastic skin, over-smoothed texture, low contrast, cluttered layout, random particles, inconsistent lighting, bad anatomy, fake reflections"
        return prompt, negative
