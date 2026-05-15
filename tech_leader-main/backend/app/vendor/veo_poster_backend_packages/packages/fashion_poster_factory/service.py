from __future__ import annotations

from uuid import uuid4

from packages.campaign_intelligence import RenderProviderRegistry
from packages.fashion_poster_factory.engines import (
    AutoCollageCompositionEngine,
    FashionScoreEngine,
    LuxuryCampaignEngine,
    TypographyHierarchyEngine,
    WinnerDNAMemory,
)


class FashionPosterFactoryService:
    def __init__(self):
        self.composition = AutoCollageCompositionEngine()
        self.typography = TypographyHierarchyEngine()
        self.campaign = LuxuryCampaignEngine()
        self.scorer = FashionScoreEngine()
        self.memory = WinnerDNAMemory()

    def generate(self, data: dict) -> dict:
        variants: list[dict] = []
        style_order = self._style_order(data.get("style", "dark_feminine"), data.get("goal", "editorial"))
        count = int(data.get("variant_count", 6))
        provider = (data.get("provider") or "mock").strip().lower()

        for i in range(count):
            style = style_order[i % len(style_order)]
            route = self.campaign.route(style, data.get("palette"))
            layout = self.composition.compose(style)
            typo = self.typography.build(
                style=style,
                headline=data.get("headline"),
                subtitle=data.get("subtitle"),
                language=data.get("language", "vi"),
            )
            prompt = self._compile_prompt(data, style, route, typo, layout)
            scores = self.scorer.score(style, route, layout, typo)
            dna = {
                "style": style,
                "palette": route["palette"],
                "hero_crop": "medium close-up" if style != "luxury" else "clean portrait",
                "typography": typo["font_logic"],
                "layout": [z["type"] for z in layout],
                "texture_stack": route["texture"],
            }
            variants.append(
                {
                    "variant_id": str(uuid4()),
                    "style_route": style,
                    "prompt": prompt,
                    "negative_prompt": self.campaign.negative_prompt(),
                    "layout": layout,
                    "typography": typo,
                    "texture_stack": route["texture"],
                    "scores": scores,
                    "dna": dna,
                }
            )

        winner = max(variants, key=lambda v: v["scores"]["total"])
        self.memory.save_if_winner(winner["dna"], winner["scores"])

        winner_render = None
        render_error = None
        if data.get("render_winner", True):
            try:
                winner_render = RenderProviderRegistry().get(provider).generate(
                    winner["prompt"],
                    {
                        "goal": data.get("goal", "editorial"),
                        "offer": data.get("goal", "editorial"),
                        "brand": data.get("identity", "Fashion Factory"),
                    },
                )
            except Exception as exc:
                render_error = str(exc)

        return {
            "winner": winner,
            "variants": variants,
            "winner_render": winner_render,
            "provider_requested": provider,
            "render_error": render_error,
            "production_notes": [
                "Render hero/model first, collage layout second.",
                "Typography must not cover eyes, lips, neck or key product/fashion details.",
                "Texture should be final layer with controlled opacity.",
                "Winner DNA is persisted when total score >= 88.",
            ],
        }

    def batch_generate(self, payloads: list[dict]) -> list[dict]:
        return [self.generate(payload) for payload in payloads]

    def _style_order(self, style: str, goal: str) -> list[str]:
        if goal == "viral":
            return ["y2k", "viral", "dark_feminine", style]
        if goal == "luxury":
            return ["luxury", "vogue", "dark_feminine", style]
        return [style, "dark_feminine", "luxury", "y2k", "vogue"]

    def _compile_prompt(self, data: dict, style: str, route: dict, typo: dict, layout: list[dict]) -> str:
        return (
            "ultra realistic high fashion editorial magazine collage poster,\n"
            f"identity: {data.get('identity', 'modern it girl')}, target audience: {data.get('target', 'gen z women')},\n"
            f"style route: {style}, palette: {', '.join(route['palette'])},\n"
            f"{route['lighting']}, premium magazine composition,\n"
            "strong central hero model, multiple secondary polaroid editorial images,\n"
            f"headline typography: {typo['h1']} / {typo['h2']},\n"
            f"controlled visual chaos, {route['noise_level']},\n"
            f"texture stack: {', '.join(route['texture'])},\n"
            f"layout map: {', '.join([z['type'] for z in layout])},\n"
            "sharp facial detail, natural skin texture, cinematic contrast, print editorial realism,\n"
            "vertical poster, agency-level fashion campaign, brand identity storytelling"
        )
