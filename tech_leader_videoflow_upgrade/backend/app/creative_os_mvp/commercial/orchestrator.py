from app.creative_os_mvp.models.schemas import CreativeRequest, CommercialReasoning
from app.creative_os_mvp.commercial.attention import AttentionRoutingEngine
from app.creative_os_mvp.commercial.typography import TypographyHierarchyEngine
from app.creative_os_mvp.commercial.product_hero import ProductHeroEngine
from app.creative_os_mvp.commercial.environment import EnvironmentReactionEngine
from app.creative_os_mvp.commercial.psychology import CommercialPsychologyEngine
from app.creative_os_mvp.commercial.print_engine import BillboardPrintEngine
from app.creative_os_mvp.commercial.category import CategoryCommercialEngine

class CommercialIntelligenceOrchestrator:
    def __init__(self):
        self.attention=AttentionRoutingEngine()
        self.typography=TypographyHierarchyEngine()
        self.product=ProductHeroEngine()
        self.env=EnvironmentReactionEngine()
        self.psych=CommercialPsychologyEngine()
        self.print=BillboardPrintEngine()
        self.category=CategoryCommercialEngine()

    def reason(self, req: CreativeRequest) -> CommercialReasoning:
        b=req.brand
        category=b.industry.lower()
        attention=self.attention.reason(req)
        typography=self.typography.reason(category, b.channel, b.objective)
        product=self.product.reason(b.product_type or b.product_name, category)
        env=self.env.reason(b.brand_dna.get("sensory_effect"), category)
        psych=self.psych.reason(category, b.objective)
        print_ready=self.print.reason(req.aspect_ratio, req.output_targets)
        cat=self.category.reason(category, b.product_type)
        scores={
            "attention": sum(x["weight"] for x in attention["scan_path"])/len(attention["scan_path"])*100,
            "typography": typography["billboard_distance_readability"]*100,
            "product_hero": 88 if product["hero_angle"] else 70,
            "environment_coherence": 84 if env["physics_responses"] else 65,
            "commercial_psychology": 86,
            "print_readiness": 82 if print_ready["print_ready"] else 76,
            "category_fit": 88 if cat["visual_dna"] else 70,
        }
        total=round(sum(scores.values())/len(scores),2)
        return CommercialReasoning(
            attention_route=attention["scan_path"], typography=typography, product_hero=product,
            environment_reaction=env, psychology=psych, billboard_print=print_ready,
            category=cat, score_breakdown=scores, total_score=total,
        )
