from app.ads_engine.schemas.contracts import AdsGenerateResponse
from app.ads_engine.services.hook_engine import HookEngine
from app.ads_engine.services.creative_compiler import CreativeCompiler

class AutoAdsGenerator:
    def __init__(self):
        self.hooks = HookEngine()
        self.compiler = CreativeCompiler()

    def generate(self, req):
        limit = max(30, req.concepts * req.hooks_per_concept * len(req.formats))
        hooks = self.hooks.generate(req.industry, req.pain_points, req.benefits, req.proof_points, limit=limit)
        variants = self.compiler.compile_variants(req, hooks)
        return AdsGenerateResponse(campaign_id=req.campaign_id, variants_count=len(variants), hooks=hooks[:req.concepts*req.hooks_per_concept], variants=variants, ab_test_plan={"test_type":"hook_visual_cta_multivariate","rule":"3 variants per test cell, read data after 6-12h, scale winner","primary_metric":"winner_score","secondary_metrics":["ctr","lead_rate","sale_rate","roas"],"kill_rule":"CTR < 0.8% after 1000 impressions or zero leads after sufficient spend","scale_rule":"winner_score >= 85 and ROAS positive","variants":[v.variant_id for v in variants]})
