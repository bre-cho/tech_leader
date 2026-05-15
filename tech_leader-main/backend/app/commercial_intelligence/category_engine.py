from __future__ import annotations
from .models import CommercialInput

CATEGORY_STRATEGIES = {
    'fmcg': {'visual_cues':['bold headline','packshot dominance','sensory effect','high contrast benefit'], 'avoid':['complex storytelling','low label clarity']},
    'beauty': {'visual_cues':['skin glow','close-up face','serum texture','soft luxury lighting'], 'avoid':['plastic skin','over-smoothing','distorted hands']},
    'cosmetics': {'visual_cues':['color payoff','lip/eye detail','packshot near face','glam reflection'], 'avoid':['wrong shade','messy product geometry']},
    'fashion': {'visual_cues':['silhouette','fabric texture','editorial pose','body proportion realism'], 'avoid':['plastic body','fabric physics errors']},
    'wellness': {'visual_cues':['natural material','soft light','calm emotion','clean whitespace'], 'avoid':['aggressive contrast','overly synthetic color']},
    'sports_grooming': {'visual_cues':['cooling motion','blue energy','wet freshness','performance attitude'], 'avoid':['soft feminine lighting','weak product scale']},
    'luxury_branding': {'visual_cues':['negative space','premium material','gold/black/champagne','slow elegance'], 'avoid':['clutter','cheap gradients']},
    'ecommerce': {'visual_cues':['product clarity','benefit badges','trust markers','offer hierarchy'], 'avoid':['unclear packshot','hidden CTA']},
    'billboard': {'visual_cues':['one big idea','giant readable type','massive product silhouette','simple contrast'], 'avoid':['small text','busy background']},
    'tiktok_ads': {'visual_cues':['face hook','motion cue','fast proof','clear CTA'], 'avoid':['static posture','slow visual read']},
    'performance_marketing': {'visual_cues':['pain-point trigger','proof','offer','CTA','before-after logic'], 'avoid':['pure aesthetics without reason to buy']},
}

class CategoryCommercialEngine:
    def strategy(self, data: CommercialInput) -> dict:
        base = CATEGORY_STRATEGIES[data.category]
        return {
            'category': data.category,
            'visual_cues': base['visual_cues'],
            'avoid': base['avoid'],
            'benefit_framing': [f"Turn benefit into visible proof: {b}" for b in data.product_benefits],
            'prompt_directive': ', '.join(base['visual_cues']) + '; avoid ' + ', '.join(base['avoid']),
        }
