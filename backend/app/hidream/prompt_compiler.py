
from __future__ import annotations
from typing import Any, Dict, List
from app.schemas.hidream import HiDreamGenerateRequest, HiDreamPromptContract

INDUSTRY_STYLE_MAP: Dict[str, Dict[str, str]] = {
    "beauty": {"lens": "85mm portrait lens", "light": "soft luxury side light with champagne highlights", "mood": "premium beauty commercial", "material": "natural skin texture, glossy cosmetic packaging, soft fabric"},
    "cosmetic": {"lens": "100mm macro product lens", "light": "controlled studio reflections, clean white-gold rim light", "mood": "high-trust cosmetic advertising", "material": "glass bottle, liquid refraction, metallic cap, skin glow"},
    "fashion": {"lens": "70mm editorial fashion lens", "light": "high-fashion spotlight with soft falloff", "mood": "editorial luxury fashion", "material": "fabric folds, silk flow, cotton tension, realistic skin"},
    "perfume": {"lens": "100mm commercial product lens", "light": "dramatic volumetric luxury lighting", "mood": "luxury fragrance hero campaign", "material": "glass, liquid, metal, condensation, crystal reflections"},
    "showroom": {"lens": "24mm architectural lens", "light": "layered interior lighting with realistic reflections", "mood": "premium spatial trust", "material": "stone, wood, glass, metal, soft upholstery"},
}

USECASE_COMPOSITION = {
    "beauty_ad": "close-up beauty composition, face and product aligned, clean CTA-safe negative space",
    "fashion_editorial": "editorial magazine cover composition, elongated silhouette, premium negative space",
    "cosmetic_product": "product hero foreground, model support frame, visible packaging, ad-safe layout",
    "luxury_perfume": "dramatic product hero, reflective surface, atmospheric depth, brand-safe label area",
    "poster": "commercial poster layout, strong hierarchy, product visible, typography-safe zones",
    "ecommerce": "clean product clarity, conversion-oriented framing, realistic scale and packaging",
    "showroom": "interior hero view, spatial depth, material harmony, premium lighting path",
    "beauty_avatar": "consistent virtual model avatar, product holding, natural expression and commercial beauty lighting",
    "storyboard_keyframe": "cinematic keyframe, motion-ready staging, clear subject-action relationship",
}

class HiDreamPromptCompiler:
    """Converts business context into a HiDream-ready premium commercial prompt contract.

    This is deliberately not a raw prompt passthrough. It enforces the hard law:
    Intent -> Brand DNA -> Visual DNA -> Camera -> Lighting -> Material -> Composition -> Provider params.
    """
    def compile(self, req: HiDreamGenerateRequest) -> HiDreamPromptContract:
        industry_key = self._match_industry(req.industry)
        style = INDUSTRY_STYLE_MAP.get(industry_key, INDUSTRY_STYLE_MAP["beauty"])
        visual = req.visual_dna or {}
        brand = req.brand_dna or {}
        camera = self._camera_grammar(req, style, visual)
        lighting = self._lighting_logic(req, style, brand)
        material = self._material_logic(req, style, visual)
        composition = self._composition_logic(req, style)
        typography = self._typography_policy(req)
        positive = self._positive_prompt(req, style, camera, lighting, material, composition, typography)
        negative = self._negative_prompt(req)
        provider_params = self._provider_params(req)
        return HiDreamPromptContract(
            positive_prompt=positive,
            negative_prompt=negative,
            camera_grammar=camera,
            lighting_logic=lighting,
            material_logic=material,
            composition_logic=composition,
            typography_policy=typography,
            provider_params=provider_params,
        )

    def _match_industry(self, industry: str) -> str:
        text = industry.lower()
        if any(k in text for k in ["cosmetic", "skincare", "makeup", "mỹ phẩm"]): return "cosmetic"
        if any(k in text for k in ["fashion", "thời trang", "lookbook"]): return "fashion"
        if any(k in text for k in ["perfume", "fragrance", "nước hoa"]): return "perfume"
        if any(k in text for k in ["showroom", "interior", "nội thất"]): return "showroom"
        return "beauty"

    def _camera_grammar(self, req, style, visual):
        return {
            "lens": visual.get("lens", style["lens"]),
            "angle": visual.get("angle", "slight low angle for confident commercial presence"),
            "framing": visual.get("framing", "hero subject centered with product clearly readable"),
            "depth_of_field": visual.get("depth_of_field", "shallow depth of field, crisp subject edges"),
            "motion_readiness": "pose and subject placement can expand into video storyboard",
        }

    def _lighting_logic(self, req, style, brand):
        palette = brand.get("palette", "premium neutral, champagne, black, soft ivory")
        return {
            "style": style["light"],
            "palette": palette,
            "shadow_policy": "deep but clean commercial shadows, no muddy skin",
            "highlight_policy": "controlled specular highlights on product and skin",
            "color_temperature": brand.get("color_temperature", "warm neutral luxury"),
        }

    def _material_logic(self, req, style, visual):
        return {
            "primary_materials": visual.get("materials", style["material"]),
            "texture_fidelity": "preserve micro texture: pores, fabric weave, glass refraction, metal reflection",
            "commercial_realism": "no plastic skin, no warped hands, no unreadable packaging",
            "render_priority": ["face fidelity", "product clarity", "material realism", "brand readability"],
        }

    def _composition_logic(self, req, style):
        return {
            "layout": USECASE_COMPOSITION.get(req.use_case, USECASE_COMPOSITION["poster"]),
            "hierarchy": "face/product first, benefit second, CTA-safe area third",
            "negative_space": "clean region reserved for final typography overlay" if req.enable_typography_safe_mode else "natural background",
            "crop_safety": "full product visible, no crop through hands/face/logo",
        }

    def _typography_policy(self, req):
        return {
            "mode": "typography-safe" if req.enable_typography_safe_mode else "image-only",
            "instruction": "leave clean negative space for final text rendered by frontend; only render brand text if explicitly provided and short",
            "copy_text": req.copy_text or "",
            "logo_policy": "preserve product label if supplied as image/reference; otherwise avoid invented brand spelling",
        }

    def _positive_prompt(self, req, style, camera, lighting, material, composition, typography) -> str:
        parts: List[str] = [
            f"Premium commercial advertising image for {req.product_name} in {req.industry}.",
            f"Business goal: {req.business_goal}.",
            f"Audience: {req.audience}.",
            style["mood"],
            composition["layout"],
            f"Camera: {camera['lens']}, {camera['angle']}, {camera['framing']}, {camera['depth_of_field']}.",
            f"Lighting: {lighting['style']}, {lighting['color_temperature']}, {lighting['shadow_policy']}, {lighting['highlight_policy']}.",
            f"Materials: {material['primary_materials']}. {material['texture_fidelity']}.",
            "Ultra realistic, cinematic, premium editorial finish, high texture fidelity, sharp commercial details.",
            typography["instruction"],
        ]
        if req.campaign_context:
            parts.append("Campaign context: " + ", ".join(f"{k}: {v}" for k, v in req.campaign_context.items()))
        return " ".join(parts)

    def _negative_prompt(self, req) -> str:
        base = [
            "low quality", "blurry", "muddy texture", "plastic skin", "over-smoothed face",
            "distorted anatomy", "warped hands", "extra fingers", "deformed product", "wrong logo",
            "unreadable text", "misspelled typography", "overexposed highlights", "flat lighting",
            "AI artifact", "uncanny face", "bad crop", "product hidden", "brand text hallucination"
        ]
        return ", ".join(base)

    def _provider_params(self, req):
        size_map = {"1:1": "1024x1024", "4:5": "1024x1280", "3:4": "960x1280", "9:16": "768x1365", "16:9": "1365x768"}
        steps = {"draft": 24, "premium": 36, "hero": 48}[req.render_tier]
        guidance = {"draft": 4.5, "premium": 5.5, "hero": 6.5}[req.render_tier]
        return {"size": size_map[req.aspect_ratio], "num_inference_steps": steps, "guidance_scale": guidance, "seed": req.seed}
