from __future__ import annotations
from .models import CommercialInput

class BillboardPrintEngine:
    def plan(self, data: CommercialInput) -> dict:
        is_print = any(x in data.export_targets for x in ['print','billboard']) or data.category == 'billboard'
        return {
            'enabled': is_print,
            'export_profiles': self._profiles(data),
            'large_format_rules': {
                'single_focal_path': True,
                'headline_min_frame_ratio': 0.18 if is_print else 0.1,
                'contrast_ratio_target': 'high',
                'cta_safe_zone': 'bottom 15% or right lower third',
                'logo_safe_zone': 'top-left/top-right, never edge-clipped',
                'cmyk_safety': is_print,
                'upscale_target': '8K print-ready' if is_print else '4K social-ready',
            },
            'qa_checks': ['distance_readability', 'logo_not_cropped', 'text_area_clean', 'artifact_free_edges', 'print_sharpness'],
        }
    def _profiles(self, data: CommercialInput) -> list[dict]:
        profiles=[]
        for t in data.export_targets:
            if t == 'billboard': profiles.append({'target':'billboard','aspect':'16:9 or 3:1','min_px':'7680x4320','notes':'very few text blocks'})
            elif t == 'print': profiles.append({'target':'print','aspect':data.aspect_ratio,'min_px':'6000px long edge','notes':'CMYK proof required by print vendor'})
            elif t == 'tiktok': profiles.append({'target':'tiktok','aspect':'9:16','min_px':'2160x3840','notes':'center-safe face/product'})
            else: profiles.append({'target':t,'aspect':data.aspect_ratio,'min_px':'2048px long edge','notes':'web optimized'})
        return profiles
