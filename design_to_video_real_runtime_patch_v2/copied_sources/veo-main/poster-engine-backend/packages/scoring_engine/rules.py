def _keyword_score(text: str, keywords: list[str], base: float, max_boost: float) -> float:
    """Return a score between *base* and *base + max_boost*.

    The boost scales linearly with the fraction of *keywords* present so that
    prompts matching more signals score proportionally higher, rather than the
    previous binary high/low approach.
    """
    if not keywords:
        return base
    matched = sum(1 for kw in keywords if kw in text)
    return base + max_boost * (matched / len(keywords))


# ─── Industry-aware keyword sets ─────────────────────────────────────────────
# Each tuple contains (product_focus_kws, luxury_kws, attention_kws,
# trust_kws, ctr_kws, conversion_kws).

_INDUSTRY_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "beauty": {
        "product_focus": ["product must dominate", "product close", "product closeup", "hero product"],
        "luxury": ["luxury", "gold", "premium", "dior", "ysl", "chanel", "cinematic"],
        "trust": ["visible skin texture", "no plastic skin", "no over-smoothing", "realistic"],
        "attention": ["split", "close-up", "closeup", "before", "after", "extreme"],
    },
    "fnb": {
        "product_focus": ["product hero", "food close-up", "plating", "macro", "appetizing"],
        "luxury": ["premium", "artisan", "chef", "gourmet", "fresh", "high-quality"],
        "trust": ["real food", "natural", "no filter", "authentic"],
        "attention": ["macro", "closeup", "steam", "drip", "overhead", "flat lay"],
    },
    "fashion": {
        "product_focus": ["outfit hero", "garment focus", "product close", "fashion detail"],
        "luxury": ["luxury", "editorial", "couture", "premium", "designer", "high fashion"],
        "trust": ["real model", "natural body", "authentic", "no retouching"],
        "attention": ["full body", "close-up", "detail shot", "movement", "dynamic"],
    },
    "tech": {
        "product_focus": ["product cgi", "device hero", "screen focus", "product highlight"],
        "luxury": ["sleek", "futuristic", "premium", "minimalist", "cutting-edge"],
        "trust": ["real specs", "demo", "ui screenshot", "benchmark"],
        "attention": ["glow", "neon", "gradient", "dynamic angle", "floating"],
    },
    "real_estate": {
        "product_focus": ["property hero", "interior focus", "space composition", "architecture"],
        "luxury": ["luxury", "premium", "gold", "elegant", "high-end", "prestigious"],
        "trust": ["real photo", "actual property", "no cgi", "authentic"],
        "attention": ["wide angle", "panoramic", "golden hour", "aerial"],
    },
    # General set – used as the fallback when the industry cannot be inferred.
    # Scores start from the same base values as all other industries so unknown
    # industries are not penalised relative to known ones.
    "general": {
        "product_focus": ["product", "hero", "focus", "highlight", "main subject"],
        "luxury": ["premium", "high quality", "professional", "clean", "polished"],
        "trust": ["authentic", "realistic", "real", "genuine"],
        "attention": ["close-up", "contrast", "bold", "striking", "clear"],
    },
}

_COMMON_CTR_KWS = ["cta", "call to action", "click", "buy", "inbox", "order"]
_COMMON_CONVERSION_KWS = ["benefit", "cta", "offer", "urgency", "deal", "conversion"]

_VARIANT_ATTENTION_BOOST = {"before_after_split", "product_closeup"}


def _get_industry(text: str) -> str:
    """Infer the industry from the prompt text using keyword heuristics."""
    if any(k in text for k in ("skin", "lipstick", "serum", "makeup", "beauty", "dior", "ysl")):
        return "beauty"
    if any(k in text for k in ("food", "drink", "beverage", "restaurant", "cafe", "watermelon")):
        return "fnb"
    if any(k in text for k in ("fashion", "outfit", "garment", "clothing", "wardrobe")):
        return "fashion"
    if any(k in text for k in ("app", "software", "saas", "device", "screen", "interface")):
        return "tech"
    if any(k in text for k in ("apartment", "villa", "property", "real estate", "interior")):
        return "real_estate"
    # Default to "general" so unrecognised industries are not unfairly penalised
    # by being scored against beauty-specific keywords.
    return "general"


def score_prompt(prompt: str, variant_type: str) -> dict:
    text = prompt.lower()
    industry = _get_industry(text)
    kws = _INDUSTRY_KEYWORDS.get(industry, _INDUSTRY_KEYWORDS["beauty"])

    product_focus = _keyword_score(text, kws["product_focus"], base=70.0, max_boost=25.0)
    luxury_score = _keyword_score(text, kws["luxury"], base=65.0, max_boost=30.0)
    trust_score = _keyword_score(text, kws["trust"], base=60.0, max_boost=35.0)
    attention_score = _keyword_score(text, kws["attention"], base=80.0, max_boost=10.0)

    if variant_type in _VARIANT_ATTENTION_BOOST:
        attention_score = min(attention_score + 4.0, 100.0)

    ctr_score = _keyword_score(text, _COMMON_CTR_KWS, base=73.0, max_boost=18.0)
    conversion_score = _keyword_score(text, _COMMON_CONVERSION_KWS, base=75.0, max_boost=18.0)

    final_score = (
        ctr_score * 0.25
        + attention_score * 0.20
        + luxury_score * 0.20
        + product_focus * 0.20
        + conversion_score * 0.15
    )

    status = "pass"
    if product_focus < 85:
        status = "block_product_focus"
    elif luxury_score < 80:
        status = "regenerate_luxury"
    elif trust_score < 80:
        status = "reduce_ai_look"

    return {
        "ctr_score": round(ctr_score, 2),
        "attention_score": round(attention_score, 2),
        "luxury_score": round(luxury_score, 2),
        "trust_score": round(trust_score, 2),
        "product_focus": round(product_focus, 2),
        "conversion_score": round(conversion_score, 2),
        "final_score": round(final_score, 2),
        "status": status,
    }
