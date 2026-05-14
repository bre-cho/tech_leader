from __future__ import annotations
from .models import CommercialInput

REACTIONS = {
    'cooling': ['mist flows diagonally', 'hair subtly reacts to airflow', 'water droplets on product', 'blue-white particles follow motion path', 'typography partially interacts without losing readability'],
    'freshness': ['soft vapor', 'clean light bloom', 'botanical particles', 'water highlights', 'airy background depth'],
    'luxury': ['slow floating particles', 'champagne glow', 'controlled reflections', 'velvet shadows', 'premium bokeh'],
    'energy': ['diagonal streaks', 'high contrast highlights', 'dynamic product shadow', 'motion particles'],
    'natural': ['leaf movement', 'soft sunlight', 'organic texture response', 'gentle haze'],
}

class EnvironmentReactionEngine:
    def plan(self, data: CommercialInput) -> dict:
        effect = (data.sensory_effect or '').lower()
        if not effect:
            if data.category in {'sports_grooming','fmcg'}: effect = 'cooling'
            elif data.category in {'beauty','wellness'}: effect = 'freshness'
            elif data.category in {'luxury_branding','fashion'}: effect = 'luxury'
            else: effect = 'energy'
        key = next((k for k in REACTIONS if k in effect), effect if effect in REACTIONS else 'freshness')
        response = REACTIONS.get(key, REACTIONS['freshness'])
        return {
            'effect': key,
            'physics_response': response,
            'coherence_rules': ['all particles follow same direction', 'lighting direction consistent', 'effects never hide logo/face/CTA', 'motion supports attention route'],
            'prompt_directive': f"environment reacts to {key}: " + '; '.join(response),
        }
