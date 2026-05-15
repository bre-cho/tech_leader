import json
from sqlalchemy.orm import Session
from app.compound_os_mvp.db import Campaign, CreativeVariant

LAYOUTS = ["minimal editorial", "face-product split", "product-dominant hero", "social proof layout"]
HOOKS = ["outcome-first", "pain-point", "aspiration", "authority proof"]
TYPOGRAPHY = ["luxury serif", "bold condensed sans", "clean modern sans", "editorial mixed type"]
STYLES = ["premium cinematic", "clean clinical", "warm emotional", "high contrast performance"]

class CampaignOS:
    def create_campaign(self, db: Session, brand, req):
        campaign = Campaign(
            brand_id=brand.id,
            name=req.campaign_name,
            product_name=req.product_name,
            product_type=req.product_type,
            audience=req.audience,
            goal=req.goal,
            channel=req.channel,
            status="running",
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    def generate_variants(self, db: Session, campaign, req, memory, graph_edges, count=3):
        variants = []
        prior_hooks = memory.get("winning_hooks", [])
        for i in range(count):
            layout = memory.get("winning_layouts", [LAYOUTS[i % len(LAYOUTS)]])[0] if i == 0 and memory.get("winning_layouts") else LAYOUTS[i % len(LAYOUTS)]
            hook = prior_hooks[0] if i == 0 and prior_hooks else HOOKS[i % len(HOOKS)]
            typography = memory.get("winning_typography", [TYPOGRAPHY[i % len(TYPOGRAPHY)]])[0] if i == 0 and memory.get("winning_typography") else TYPOGRAPHY[i % len(TYPOGRAPHY)]
            style = STYLES[i % len(STYLES)]
            offer = req.offer or "Try today"

            prompt = self._compile_prompt(req, layout, hook, typography, style, graph_edges)
            storyboard = [
                {"scene": 1, "purpose": "attention", "visual": hook, "duration": 2},
                {"scene": 2, "purpose": "desire", "visual": f"{req.product_name} product hero", "duration": 3},
                {"scene": 3, "purpose": "trust", "visual": "proof / texture / benefit", "duration": 3},
                {"scene": 4, "purpose": "conversion", "visual": offer, "duration": 2},
            ]

            score = self._score_variant(layout, hook, typography, style, graph_edges)
            variant = CreativeVariant(
                campaign_id=campaign.id,
                name=f"Variant {i+1}",
                layout=layout,
                hook=hook,
                typography=typography,
                visual_style=style,
                offer=offer,
                prompt=prompt,
                storyboard_json=json.dumps(storyboard),
                score=score,
            )
            db.add(variant)
            variants.append(variant)
        db.commit()
        for v in variants:
            db.refresh(v)
        return variants

    def _compile_prompt(self, req, layout, hook, typography, style, graph_edges):
        graph_logic = "; ".join([f"{e.source} {e.relation} {e.target}" for e in graph_edges[:5]])
        return f'''
AI-Native Creative Business OS campaign asset.
Brand: {req.brand_name}. Industry: {req.industry}. Product: {req.product_name}.
Audience: {req.audience}. Goal: {req.goal}. Channel: {req.channel}.
Layout: {layout}. Hook logic: {hook}. Typography: {typography}. Visual style: {style}.
Creative Intelligence Graph logic: {graph_logic}.
Commercial visual route: first glance → emotional trigger → product hero → trust proof → CTA.
Generate a premium, realistic, conversion-oriented campaign visual with typography-safe regions,
product clarity, brand consistency, and poster-to-video storyboard readiness.
'''.strip()

    def _score_variant(self, layout, hook, typography, style, graph_edges):
        score = 60
        if "minimal" in layout: score += 8
        if "outcome" in hook: score += 10
        if "luxury" in typography or "bold" in typography: score += 7
        if "premium" in style or "cinematic" in style: score += 8
        score += min(7, int(sum(e.weight for e in graph_edges[:5])))
        return min(100, float(score))
