from __future__ import annotations
from .models import CommercialInput, VisualZone

class TypographyHierarchyEngine:
    def plan(self, data: CommercialInput, zones: list[VisualZone]) -> dict:
        billboard = 'billboard' in data.export_targets or data.category == 'billboard'
        tiktok = 'tiktok' in data.export_targets or data.category == 'tiktok_ads'
        luxury = data.price_tier == 'luxury' or data.category in {'luxury_branding','beauty','fashion'}
        headline_style = 'ultra-bold condensed sans-serif' if billboard or data.category in {'fmcg','sports_grooming'} else 'elegant high-contrast serif' if luxury else 'bold clean sans-serif'
        min_ratio = 0.18 if billboard else 0.12 if tiktok else 0.09
        text_policy = 'real text can be rendered in frontend overlay for perfect fidelity; image prompt reserves clean typography area'
        return {
            'headline_style': headline_style,
            'headline_scale_frame_ratio': min_ratio,
            'hierarchy': ['headline', 'product benefit', 'brand/logo', 'CTA'],
            'spacing': 'tight high-impact spacing' if billboard else 'premium editorial spacing' if luxury else 'clean commercial spacing',
            'readability_rules': {
                'billboard_distance_readable': billboard,
                'high_contrast_required': True,
                'avoid_text_on_busy_background': True,
                'safe_area_margin_percent': 8 if billboard else 6,
                'max_text_blocks': 3 if billboard else 5,
            },
            'text_policy': text_policy,
            'prompt_directive': f"reserve a clean readable typography area, {headline_style}, strong visual weight, no distorted text",
        }
