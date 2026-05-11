from __future__ import annotations
import hashlib
from app.ads_engine.core.presets import INDUSTRY_PRESETS, DEFAULT_STYLE, DEFAULT_MOTION
from app.ads_engine.schemas.contracts import CreativeVariant

class CreativeCompiler:
    def _id(self, text): return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]

    @staticmethod
    def _resolve_provider(provider_preference: str | None) -> str:
        provider = (provider_preference or "").strip().lower()
        if not provider:
            raise ValueError(
                "provider_preference is required for ads creative compilation; "
                "refusing implicit fallback provider."
            )
        return provider

    def compile_variants(self, req, hooks):
        preset = INDUSTRY_PRESETS.get(req.industry, INDUSTRY_PRESETS["saas"])
        concepts = preset["concepts"][:max(1, req.concepts)]
        style = req.style or DEFAULT_STYLE
        motion = req.motion or DEFAULT_MOTION
        provider = self._resolve_provider(req.provider_preference)
        character = req.character or {"id":"char_default_presenter","role":"expert","face":"consistent realistic presenter","outfit":"clean modern outfit"}
        variants, hi = [], 0
        for concept in concepts:
            for fmt in req.formats:
                for _ in range(req.hooks_per_concept):
                    hook = hooks[hi % len(hooks)]; hi += 1
                    base = f"{preset['visual_style']}, concept={concept['name']}, visual={concept['visual']}, product={req.product_name}, offer={req.offer or ''}, audience={req.audience}, clear CTA area, high contrast"
                    image_prompt = f"high converting advertising image, {base}, headline: {hook.hook}, CTA: {req.cta}, format {fmt}, ultra realistic, premium design"
                    video_prompt = f"dynamic marketing video ad, {base}, hook first 2 seconds: {hook.hook}, demo/result reveal, final CTA: {req.cta}, motion template: {motion}, same character DNA: {character}"
                    negative = "too much text, cluttered layout, unreadable Vietnamese, watermark, random logo, inconsistent character, flat lighting, low contrast, generic stock photo"
                    vid = f"{req.campaign_id}_{self._id(concept['name'] + hook.hook + fmt)}"
                    payload = {"project_id":req.campaign_id,"provider":provider,"aspect_ratio":fmt,"character":character,"style":style,"motion":motion,"brief":{"hook":hook.hook,"cta":req.cta,"product":req.product_name,"offer":req.offer,"concept":concept,"image_prompt":image_prompt,"video_prompt":video_prompt,"negative_prompt":negative}}
                    variants.append(CreativeVariant(variant_id=vid, concept_name=concept["name"], hook=hook.hook, format=fmt, platform=req.platform, image_prompt=image_prompt, video_prompt=video_prompt, negative_prompt=negative, cta=req.cta, predicted_ctr_score=round(min(99, hook.score*0.58+35),2), predicted_conversion_score=round(min(99, hook.score*0.42+38),2), render_payload=payload))
        return variants
