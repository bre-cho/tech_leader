from __future__ import annotations
from .models import CommercialInput

ANGLE_BY_CATEGORY = {
    'cosmetics': 'close 3/4 hero packshot near face, label visible',
    'beauty': 'foreground serum bottle 3/4 perspective with glass refraction',
    'fmcg': 'large packshot angled toward camera, condensation and crisp label',
    'sports_grooming': 'dynamic bottle hero perspective, metallic highlights, water droplets',
    'fashion': 'product worn or held naturally, editorial catalog framing',
    'ecommerce': 'front-facing product clarity with slight 3/4 depth',
}

MATERIAL_RULES = {
    'glass': 'realistic refraction, sharp rim highlights, transparent depth',
    'metal': 'controlled metallic specular highlights, premium edge reflections',
    'plastic': 'clean FMCG shine, realistic molded surface',
    'liquid': 'subtle meniscus, translucency, luxury glow',
    'fabric': 'visible weave, natural folds, realistic tension',
    'paper': 'print-safe texture, clean label sharpness',
}

class ProductHeroEngine:
    def plan(self, data: CommercialInput) -> dict:
        materials = data.product_materials or (['glass','liquid'] if data.category in {'beauty','cosmetics'} else ['plastic'] if data.category in {'fmcg','sports_grooming'} else ['fabric'] if data.category == 'fashion' else ['paper'])
        material_logic = [MATERIAL_RULES.get(m.lower(), f'realistic {m} material response') for m in materials]
        hero = ANGLE_BY_CATEGORY.get(data.category, 'premium 3/4 product hero perspective')
        return {
            'hero_angle': hero,
            'logo_policy': 'product logo/label must remain visible, unwarped, not covered by hands/effects',
            'material_logic': material_logic,
            'reflection_policy': 'match product reflections to environment lighting and camera angle',
            'commercial_packshot_rules': ['sharp silhouette', 'label readability', 'premium highlight control', 'clean foreground separation'],
            'prompt_directive': f"{hero}, {', '.join(material_logic)}, crisp product edges, premium reflections, label clarity",
        }
