from __future__ import annotations
from .models import CommercialInput

PSYCHOLOGY = {
    'cooling': {'emotion':'cold freshness','perception':'anti-heat, anti-dandruff, clean performance','colors':['icy blue','white','silver']},
    'freshness': {'emotion':'clean renewal','perception':'wellness, purity, natural care','colors':['soft green','white','aqua']},
    'luxury': {'emotion':'premium desire','perception':'high value, elegance, exclusivity','colors':['black','champagne gold','cream']},
    'clinical': {'emotion':'trust and safety','perception':'proof, dermatology, professional care','colors':['white','navy','soft blue']},
    'energy': {'emotion':'dopamine and action','perception':'performance, youth, vitality','colors':['electric blue','red accent','black']},
}

CATEGORY_DEFAULTS = {
    'beauty': 'luxury', 'cosmetics':'luxury', 'wellness':'freshness', 'sports_grooming':'cooling', 'fmcg':'energy', 'luxury_branding':'luxury', 'ecommerce':'clinical', 'fashion':'luxury'
}

class CommercialPsychologyEngine:
    def map(self, data: CommercialInput) -> dict:
        key = CATEGORY_DEFAULTS.get(data.category, 'freshness')
        if data.sensory_effect:
            low = data.sensory_effect.lower()
            key = next((k for k in PSYCHOLOGY if k in low), key)
        profile = PSYCHOLOGY[key]
        return {
            'primary_psychology': key,
            **profile,
            'buying_logic': self._buying_logic(data),
            'trust_signals': self._trust(data),
            'dopamine_triggers': self._dopamine(data),
        }
    def _buying_logic(self, data: CommercialInput) -> list[str]:
        if data.category in {'beauty','cosmetics'}: return ['visible skin result', 'premium texture', 'close-up proof', 'aspirational identity']
        if data.category == 'sports_grooming': return ['instant freshness', 'performance confidence', 'cooling sensation']
        if data.category == 'ecommerce': return ['clear product', 'benefit badges', 'offer clarity', 'trust proof']
        return ['clear benefit', 'brand recall', 'high contrast desire trigger']
    def _trust(self, data: CommercialInput) -> list[str]:
        return ['clean lighting', 'label clarity', 'natural texture', 'not overgenerated', 'commercial realism']
    def _dopamine(self, data: CommercialInput) -> list[str]:
        return ['diagonal motion', 'spark highlights', 'sensory particles', 'hero reveal', 'micro contrast']
