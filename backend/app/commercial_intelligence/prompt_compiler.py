from __future__ import annotations
from .models import CommercialInput, VisualZone

class CommercialPromptCompiler:
    def compile(self, data: CommercialInput, zones: list[VisualZone], typography: dict, product: dict, env: dict, psych: dict, billboard: dict, category: dict) -> tuple[str,str]:
        route = ' -> '.join([z.name for z in zones])
        headline = data.headline or f"{data.product_name} for {data.audience}"
        cta = data.cta or 'Khám phá ngay'
        prompt = f"""
Premium commercial advertising visual for {data.brand_name} {data.product_name}, category: {data.category}.
Commercial visual reasoning: guide the viewer eye route as {route}; first hook must be instantly readable, product must become the desire anchor, CTA area must stay clean and conversion-focused.
Headline concept: {headline}. CTA concept: {cta}.
Category-specific commercial intelligence: {category['prompt_directive']}.
Product hero: {product['prompt_directive']}; product logo/label visible and undistorted.
Typography intelligence: {typography['prompt_directive']}; keep clean text-safe zones for final typography overlay.
Environment reaction system: {env['prompt_directive']}; all effects react coherently and support the attention route.
Commercial psychology: evoke {psych['emotion']} to create {psych['perception']}; colors: {', '.join(psych['colors'])}; buying logic: {', '.join(psych['buying_logic'])}.
Lighting and composition: cinematic commercial photography, strong depth, realistic material response, high contrast but premium, sharp foreground separation, {data.aspect_ratio} aspect ratio.
Export intent: {', '.join(data.export_targets)}; print/readability rules: {billboard['large_format_rules']}.
Ultra realistic, commercial-grade, premium campaign finish, no watermark, no distorted text, no broken product geometry.
""".strip()
        negative = "distorted logo, unreadable text, warped packaging, extra fingers, plastic skin, low-resolution, cluttered CTA, random particles, inconsistent lighting, fake reflections, cropped product, deformed face, overgenerated AI look"
        return prompt, negative
