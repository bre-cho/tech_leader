from __future__ import annotations
from .models import CommercialInput, VisualZone

CATEGORY_ROUTE = {
    'beauty': ['face','skin_glow','product','headline','cta'],
    'cosmetics': ['face','lips_or_skin','product','benefit_text','cta'],
    'fmcg': ['headline','product','sensory_effect','benefit_text','cta'],
    'sports_grooming': ['headline','cooling_motion','face','product','cta'],
    'fashion': ['silhouette','face','fabric','brand_text','cta'],
    'wellness': ['emotion','natural_element','product','benefit_text','cta'],
    'luxury_branding': ['brand_symbol','product','premium_material','headline','cta'],
    'ecommerce': ['product','benefit_badges','price_or_offer','cta','trust_signal'],
    'billboard': ['headline','product','brand_logo','single_benefit','cta'],
    'tiktok_ads': ['face_expression','motion_hook','product','proof','cta'],
    'performance_marketing': ['pain_point','product','proof','offer','cta'],
}

ROLE_MAP = {
    'headline': ('first visual hook', 'top third / oversized readable block', 'attention'),
    'product': ('desire trigger and memory anchor', 'center-right hero 3/4 angle', 'conversion'),
    'face': ('emotional anchor and trust', 'left or center close-up', 'trust'),
    'skin_glow': ('beauty proof', 'cheek/highlight region', 'proof'),
    'cta': ('action focus', 'bottom safe zone', 'conversion'),
    'cooling_motion': ('dopamine motion cue', 'diagonal airflow path', 'retention'),
    'sensory_effect': ('sensory imagination', 'around product without blocking logo', 'dopamine'),
    'benefit_text': ('reason to believe', 'secondary text zone', 'trust'),
    'proof': ('conversion proof', 'near product or lower third', 'conversion'),
    'offer': ('buying urgency', 'CTA cluster', 'conversion'),
    'brand_logo': ('brand recall', 'top-left or packshot label area', 'recall'),
}

class AttentionRoutingEngine:
    """Builds a deterministic visual attention route: what the eye sees first, second, and why."""
    def route(self, data: CommercialInput) -> list[VisualZone]:
        tokens = CATEGORY_ROUTE.get(data.category, ['headline','product','cta'])
        zones: list[VisualZone] = []
        for i, token in enumerate(tokens):
            role, pos, conv = ROLE_MAP.get(token, (f'{token} visual cue', 'balanced composition zone', 'support'))
            base = max(0.15, 1.0 - i * 0.13)
            if token in {'product','cta'} and data.business_goal.lower() in {'sales','conversion','lead','purchase'}:
                base += 0.08
            zones.append(VisualZone(
                name=token,
                role=role,
                priority=i + 1,
                suggested_position=pos,
                attention_weight=round(min(base, 1.0), 3),
                conversion_role=conv,
            ))
        return zones

    def summarize(self, zones: list[VisualZone]) -> str:
        return ' → '.join([z.name for z in sorted(zones, key=lambda x: x.priority)])
