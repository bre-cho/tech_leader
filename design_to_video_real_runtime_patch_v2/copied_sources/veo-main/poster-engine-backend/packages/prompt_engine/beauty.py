VARIANT_TYPES = [
    "luxury_hero",
    "before_after_split",
    "product_closeup",
    "model_desire_shot",
    "conversion_cta",
]

def build_beauty_prompt(product_name: str, offer: str, brand_voice: str, variant_type: str) -> str:
    base = f"""
Ultra high-end luxury beauty advertising poster for {product_name}.
Style: {brand_voice}, premium Dior / YSL / Chanel beauty campaign aesthetic.
Hero product must dominate the composition. Text is small and secondary.
Realistic Asian female model, visible skin texture, no over-smoothing, no plastic skin.
Cinematic black / deep navy background, gold highlights, controlled studio lighting.
CTA: {offer}.
Vertical 4:5, commercial ad poster, clean composition, high conversion.
Negative rules: no clutter, no oversized headline, no unrealistic body, no AI plastic skin.
""".strip()
    variant_map = {
        "luxury_hero": "Premium hero shot, product close to face, elegant confidence, luxury glow.",
        "before_after_split": "Split-lip before/after effect: natural pale side versus rich product result side.",
        "product_closeup": "Extreme product close-up, metallic reflection, sharp engraving, luxury packaging detail.",
        "model_desire_shot": "Confident model holding product close to camera, beauty campaign desire trigger.",
        "conversion_cta": "Clear product benefit icons, visible CTA button, still premium and minimal.",
    }
    return base + "\n" + variant_map.get(variant_type, "Luxury campaign poster.")

def _validate_prompt_business_rules(prompt: str, variant_type: str) -> None:
    """Enforce business-level content rules on generated prompts.

    Raises ValueError so callers get a clear non-retryable error before
    hitting any provider.
    """
    lower = prompt.lower()
    if "product" not in lower:
        raise ValueError(
            f"Prompt for variant '{variant_type}' must reference the product. "
            "Check build_beauty_prompt()."
        )
    if "cta" not in lower and "offer" not in lower:
        raise ValueError(
            f"Prompt for variant '{variant_type}' must include a CTA or offer. "
            "Check build_beauty_prompt()."
        )


def generate_variant_prompts(project: dict, brand: dict) -> list[dict]:
    prompts = [
        {
            "variant_type": vt,
            "prompt": build_beauty_prompt(
                product_name=project["product_name"],
                offer=project.get("offer", "Inbox chọn màu theo cá tính"),
                brand_voice=brand.get("brand_voice", "luxury, premium, trustworthy"),
                variant_type=vt,
            ),
        }
        for vt in VARIANT_TYPES
    ]
    for item in prompts:
        _validate_prompt_business_rules(item["prompt"], item["variant_type"])
    return prompts
