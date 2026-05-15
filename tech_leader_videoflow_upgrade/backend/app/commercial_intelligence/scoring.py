from __future__ import annotations
from .models import CommercialInput, VisualZone

class CommercialScoringEngine:
    def score(self, data: CommercialInput, zones: list[VisualZone], typography: dict, product: dict, env: dict, psych: dict, billboard: dict, category: dict) -> dict[str,float]:
        attention = min(100, 55 + sum(z.attention_weight*5 for z in zones) + (8 if env['effect'] else 0))
        trust = 62 + len(psych.get('trust_signals', []))*4 + (8 if 'label clarity' in product.get('logo_policy','') else 0)
        conversion = 55 + sum(1 for z in zones if z.conversion_role=='conversion')*7 + len(psych.get('buying_logic', []))*3
        typography_score = 68 + (12 if typography['readability_rules']['high_contrast_required'] else 0) + (10 if typography['readability_rules']['billboard_distance_readable'] else 0)
        product_score = 70 + len(product.get('commercial_packshot_rules', []))*4
        print_score = 60 + (25 if billboard.get('enabled') else 10)
        category_fit = 70 + min(20, len(category.get('visual_cues', []))*3)
        final = round(attention*.18 + trust*.16 + conversion*.20 + typography_score*.12 + product_score*.14 + print_score*.08 + category_fit*.12, 2)
        return {k: round(min(v,100),2) for k,v in {
            'attention_score': attention,
            'trust_score': trust,
            'conversion_score': conversion,
            'typography_score': typography_score,
            'product_hero_score': product_score,
            'print_readiness_score': print_score,
            'category_fit_score': category_fit,
            'final_commercial_score': final,
        }.items()}

class CommercialQAEngine:
    def verify(self, scores: dict[str,float], data: CommercialInput) -> dict:
        blocks=[]; warnings=[]
        if scores['attention_score'] < 70: blocks.append('attention_route_too_weak')
        if scores['conversion_score'] < 70 and data.business_goal.lower() in {'sales','conversion','purchase','lead'}: blocks.append('conversion_path_too_weak')
        if scores['typography_score'] < 75 and ('billboard' in data.export_targets or data.category=='billboard'): blocks.append('billboard_typography_not_ready')
        if scores['product_hero_score'] < 78: warnings.append('product_packshot_needs_stronger_hero_rules')
        passed = not blocks
        return {'passed': passed, 'blocks': blocks, 'warnings': warnings, 'promotion_status': 'APPROVED' if passed and scores['final_commercial_score'] >= 80 else 'NEEDS_REVISION'}
