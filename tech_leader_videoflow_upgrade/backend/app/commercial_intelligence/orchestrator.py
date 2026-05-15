from __future__ import annotations
from dataclasses import asdict
from .models import CommercialInput, ReasoningResult, artifact_contract, stable_id
from .attention_routing import AttentionRoutingEngine
from .typography import TypographyHierarchyEngine
from .product_hero import ProductHeroEngine
from .environment_reaction import EnvironmentReactionEngine
from .psychology import CommercialPsychologyEngine
from .billboard_print import BillboardPrintEngine
from .category_engine import CategoryCommercialEngine
from .scoring import CommercialScoringEngine, CommercialQAEngine
from .prompt_compiler import CommercialPromptCompiler

class CommercialVisualReasoningOrchestrator:
    """V27.1-V27.7 hardcoded commercial intelligence runtime.
    This is not a prompt template. It builds a graph of attention, category logic,
    product hero rules, typography, environment reaction, psychology and print QA.
    """
    def __init__(self):
        self.attention = AttentionRoutingEngine(); self.typography = TypographyHierarchyEngine(); self.product = ProductHeroEngine()
        self.environment = EnvironmentReactionEngine(); self.psychology = CommercialPsychologyEngine(); self.billboard = BillboardPrintEngine()
        self.category = CategoryCommercialEngine(); self.scoring = CommercialScoringEngine(); self.qa = CommercialQAEngine(); self.compiler = CommercialPromptCompiler()

    def run(self, data: CommercialInput) -> ReasoningResult:
        zones = self.attention.route(data)
        typo = self.typography.plan(data, zones)
        product = self.product.plan(data)
        env = self.environment.plan(data)
        psych = self.psychology.map(data)
        bill = self.billboard.plan(data)
        cat = self.category.strategy(data)
        prompt, negative = self.compiler.compile(data, zones, typo, product, env, psych, bill, cat)
        scores = self.scoring.score(data, zones, typo, product, env, psych, bill, cat)
        qa = self.qa.verify(scores, data)
        payload = {'input': asdict(data), 'scores': scores, 'route': [asdict(z) for z in zones], 'prompt': prompt}
        contract = artifact_contract('commercial_visual_reasoning_plan', payload)
        storyboard = self._storyboard(data, zones, psych)
        winner_dna = self._winner_dna(data, scores, zones, cat, psych)
        return ReasoningResult(
            attention_route=zones, typography=typo, product_hero=product, environment_reaction=env,
            psychology=psych, billboard_print=bill, category_strategy=cat, prompt=prompt, negative_prompt=negative,
            scores=scores, qa=qa, artifact_contract=contract, storyboard=storyboard, winner_dna=winner_dna
        )

    def _storyboard(self, data: CommercialInput, zones, psych) -> list[dict]:
        return [
            {'scene':1,'name':'Attention Hook','visual':f"Open on {zones[0].name} with {psych['emotion']}", 'duration_sec':2},
            {'scene':2,'name':'Product Hero','visual':f"Reveal {data.product_name} with premium product hero angle", 'duration_sec':3},
            {'scene':3,'name':'Benefit Proof','visual':'; '.join(data.product_benefits[:3]) or 'show visible product benefit', 'duration_sec':4},
            {'scene':4,'name':'Trust / Desire','visual':f"Use {psych['perception']} signals and realistic commercial detail", 'duration_sec':3},
            {'scene':5,'name':'CTA','visual':data.cta or 'Clear CTA end card', 'duration_sec':3},
        ]

    def _winner_dna(self, data, scores, zones, cat, psych) -> dict:
        return {
            'dna_id': stable_id('winner_dna_candidate', {'brand':data.brand_name,'product':data.product_name,'category':data.category,'scores':scores}),
            'category': data.category,
            'attention_route': [z.name for z in zones],
            'visual_cues': cat['visual_cues'],
            'psychology': psych['primary_psychology'],
            'score': scores['final_commercial_score'],
            'store_candidate': scores['final_commercial_score'] >= 85,
        }
