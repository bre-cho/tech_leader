from apps.api.core.config import settings
from packages.provider_adapters.adobe import AdobeMockAdapter, AdobeProductionAdapter
from packages.provider_adapters.canva import CanvaMockAdapter, CanvaProductionAdapter


class CreativeSkillEngine:
    def list_skills(self) -> list[dict]:
        return [
            {
                "id": "attention_dominance",
                "name": "Attention Dominance Skill",
                "meaning": "Stop-scroll bang contrast, focal isolation, typography dominance.",
            },
            {
                "id": "luxury_editorial",
                "name": "Luxury Editorial Skill",
                "meaning": "Premium perception bang serif, whitespace, cinematic lighting.",
            },
            {
                "id": "product_environment_storytelling",
                "name": "Product Environment Storytelling Skill",
                "meaning": "Dat san pham vao boi canh co narrative va emotional atmosphere.",
            },
            {
                "id": "ingredient_transformation",
                "name": "Ingredient Transformation Skill",
                "meaning": "Bien nguyen lieu thanh visual story tang trust va brand recall.",
            },
            {
                "id": "y2k_magazine_collage",
                "name": "Y2K Magazine Collage Skill",
                "meaning": "Controlled chaos, polaroid layers, magazine scrapbook energy.",
            },
        ]

    def select(
        self,
        industry: str,
        goal: str,
        audience: str,
        perception_targets: list[str],
    ) -> list[dict]:
        skills = self.list_skills()
        joined = " ".join([industry, goal, audience, *perception_targets]).lower()
        selected = []
        if any(keyword in joined for keyword in ["luxury", "premium", "fashion", "beauty"]):
            selected.append(skills[1])
        if any(keyword in joined for keyword in ["viral", "thumbnail", "genz", "attention"]):
            selected.append(skills[0])
        if any(keyword in joined for keyword in ["ingredient", "trust", "food", "beverage"]):
            selected.append(skills[3])
        if any(keyword in joined for keyword in ["y2k", "magazine", "editorial", "collage"]):
            selected.append(skills[4])
        return selected or [skills[2]]


class DesignSystemRegistry:
    def list_systems(self) -> list[dict]:
        return [
            {
                "id": "luxury_editorial",
                "name": "Luxury Editorial",
                "palette": ["black", "ivory", "deep red", "gold accent"],
                "typography": {"h1": "high contrast serif", "body": "minimal sans"},
                "spacing": "large whitespace",
                "composition": "hero isolation + editorial balance",
                "lighting": "soft cinematic directional",
                "texture": "subtle grain premium paper",
            },
            {
                "id": "tech_vortex",
                "name": "Tech Vortex",
                "palette": ["midnight blue", "neon cyan", "silver"],
                "typography": {"h1": "geometric sans", "body": "condensed sans"},
                "spacing": "controlled dense",
                "composition": "centered product + energy vortex",
                "lighting": "neon rim light",
                "texture": "hologram + particles",
            },
            {
                "id": "y2k_collage",
                "name": "Y2K Magazine Collage",
                "palette": ["black", "white", "red", "pink accent"],
                "typography": {"h1": "oversized condensed", "body": "mixed editorial"},
                "spacing": "controlled chaos",
                "composition": "hero portrait + polaroids + stickers",
                "lighting": "flash editorial",
                "texture": "ripped paper + tape + xerox grain",
            },
            {
                "id": "clean_commerce",
                "name": "Clean Commerce",
                "palette": ["white", "brand color", "contrast accent"],
                "typography": {"h1": "bold sans", "body": "readable sans"},
                "spacing": "conversion clarity",
                "composition": "product dominance + CTA gravity",
                "lighting": "high-key studio",
                "texture": "clean shadow",
            },
        ]

    def select(self, industry: str, goal: str, perception_targets: list[str]) -> dict:
        joined = " ".join([industry, goal, *perception_targets]).lower()
        systems = self.list_systems()
        if any(keyword in joined for keyword in ["luxury", "premium", "editorial", "fashion", "beauty"]):
            return systems[0]
        if any(keyword in joined for keyword in ["tech", "futuristic", "innovation"]):
            return systems[1]
        if any(keyword in joined for keyword in ["y2k", "collage", "genz"]):
            return systems[2]
        return systems[3]


class PerceptionEngine:
    def route(
        self,
        industry: str,
        product: str,
        goal: str,
        audience: str,
        perception_targets: list[str],
    ) -> dict:
        targets = perception_targets or []
        industry_lower = industry.lower()
        if not targets:
            if "beauty" in industry_lower or "fashion" in industry_lower:
                targets = ["luxury", "desire", "editorial"]
            elif "tech" in industry_lower:
                targets = ["innovation", "precision", "speed"]
            elif "food" in industry_lower:
                targets = ["appetite", "warmth", "trust"]
            else:
                targets = ["clarity", "trust", "conversion"]
        return {
            "primary": targets[0],
            "secondary": targets[1:],
            "reasoning": f"Product '{product}' for audience '{audience}' should create {', '.join(targets)} perception.",
            "risk": "Avoid generic AI image output; preserve clear focal hierarchy and brand consistency.",
            "goal": goal,
        }


class CompositionEngine:
    def build(self, design_system: dict, perception: dict, platform: str) -> dict:
        primary = perception.get("primary", "trust")
        if primary in ["luxury", "editorial", "desire"]:
            layout = "luxury hero isolation"
            eye_flow = ["hero image", "headline", "secondary detail", "soft CTA"]
            safe_zones = {"headline": "top-left/top-center", "cta": "bottom-right", "face": "do-not-cover"}
        elif primary in ["innovation", "speed"]:
            layout = "center product with dynamic energy field"
            eye_flow = ["energy effect", "product", "headline", "CTA"]
            safe_zones = {"headline": "top", "cta": "bottom", "product": "center"}
        else:
            layout = "product dominance commerce layout"
            eye_flow = ["product", "benefit", "CTA"]
            safe_zones = {"product": "center", "headline": "top", "cta": "bottom"}
        return {
            "layout": layout,
            "grid": "12-column adaptive",
            "safe_zones": safe_zones,
            "eye_flow": eye_flow,
            "layer_order": ["background", "atmosphere", "hero", "fx", "typography", "cta", "texture"],
            "platform": platform,
            "composition_style": design_system.get("composition"),
        }


class TypographyEngine:
    def build(self, design_system: dict, goal: str) -> dict:
        typography = design_system.get("typography", {})
        design_system_id = design_system.get("id", "")
        if "luxury" in design_system_id:
            hierarchy = "soft authority"
            cta_behavior = "minimal premium CTA"
        elif "y2k" in design_system_id:
            hierarchy = "oversized expressive headline"
            cta_behavior = "sticker-like CTA"
        else:
            hierarchy = "conversion clarity"
            cta_behavior = "high contrast CTA"
        return {
            "h1_style": typography.get("h1", "bold sans"),
            "body_style": typography.get("body", "readable sans"),
            "hierarchy": hierarchy,
            "cta_behavior": cta_behavior,
            "goal": goal,
            "rules": [
                "H1 readable at thumbnail size",
                "Avoid covering face/product hero zone",
                "CTA must not compete with product unless direct response",
            ],
        }


class CreativeIntelligenceGraph:
    def build(self, session: dict, parts: dict) -> dict:
        return {
            "nodes": [
                {"id": "intent", "type": "user_intent", "label": session["goal"]},
                {"id": "perception", "type": "perception", "label": parts["perception"]["primary"]},
                {"id": "skill", "type": "skill", "label": ",".join(item["id"] for item in parts["skills"])},
                {"id": "design_system", "type": "design_system", "label": parts["design_system"]["id"]},
                {"id": "composition", "type": "composition", "label": parts["composition"]["layout"]},
                {"id": "typography", "type": "typography", "label": parts["typography"]["hierarchy"]},
                {"id": "prompt_stack", "type": "render_instruction", "label": "provider-ready prompt stack"},
            ],
            "edges": [
                {"from": "intent", "to": "perception", "meaning": "business intent selects perception"},
                {"from": "perception", "to": "skill", "meaning": "perception activates creative skills"},
                {"from": "skill", "to": "design_system", "meaning": "skills select visual operating rules"},
                {"from": "design_system", "to": "composition", "meaning": "design system constrains layout behavior"},
                {"from": "composition", "to": "typography", "meaning": "layout defines safe text hierarchy"},
                {"from": "typography", "to": "prompt_stack", "meaning": "typography becomes generation constraints"},
            ],
        }


class CreativeDirectorBrain:
    def __init__(self) -> None:
        self.skills = CreativeSkillEngine()
        self.registry = DesignSystemRegistry()
        self.perception = PerceptionEngine()
        self.composition = CompositionEngine()
        self.typography = TypographyEngine()
        self.graph = CreativeIntelligenceGraph()

    def plan(self, session: dict) -> dict:
        perception = self.perception.route(
            session["industry"],
            session["product"],
            session["goal"],
            session["audience"],
            session.get("perception_targets", []),
        )
        skills = self.skills.select(
            session["industry"],
            session["goal"],
            session["audience"],
            session.get("perception_targets", []),
        )
        design_system = self.registry.select(
            session["industry"],
            session["goal"],
            session.get("perception_targets", []),
        )
        composition = self.composition.build(design_system, perception, session["platform"])
        typography = self.typography.build(design_system, session["goal"])
        visual_fx = {
            "lighting": design_system["lighting"],
            "texture": design_system["texture"],
            "effects": ["subtle depth", "brand-consistent atmosphere"],
        }
        prompt_stack = {
            "system": "Create a brand-grade advertising visual based on structured creative direction.",
            "creative_prompt": (
                f"Product: {session['product']}. Industry: {session['industry']}. "
                f"Perception: {perception['primary']}. Design system: {design_system['name']}. "
                f"Composition: {composition['layout']}. Typography: {typography['hierarchy']}. "
                f"Lighting: {design_system['lighting']}. Palette: {', '.join(design_system['palette'])}."
            ),
            "negative_prompt": "generic layout, unreadable text, distorted product, cluttered composition, broken anatomy, fake plastic skin",
            "constraints": {
                "safe_zones": composition["safe_zones"],
                "eye_flow": composition["eye_flow"],
                "typography_rules": typography["rules"],
            },
        }
        parts = {
            "perception": perception,
            "skills": skills,
            "design_system": design_system,
            "composition": composition,
            "typography": typography,
        }
        return {
            "creative_direction": perception,
            "selected_skills": skills,
            "design_system": design_system,
            "composition_plan": composition,
            "typography_plan": typography,
            "visual_fx_plan": visual_fx,
            "prompt_stack": prompt_stack,
            "graph": self.graph.build(session, parts),
        }


class PosterScoringEngine:
    def score(self, plan: dict) -> dict:
        design_system = plan.get("design_system", {})
        composition = plan.get("composition_plan", {})
        typography = plan.get("typography_plan", {})
        perception = plan.get("creative_direction", {})
        luxury = 70 + (18 if "luxury" in design_system.get("id", "") else 0) + (6 if "whitespace" in design_system.get("spacing", "") else 0)
        readability = 82 + (8 if "readable" in str(typography).lower() else 0) - (4 if "oversized" in str(typography).lower() else 0)
        ctr = 78 + (10 if perception.get("primary") in ["viral", "attention", "desire", "innovation"] else 0) + (5 if "product" in str(composition).lower() else 0)
        brand_recall = 75 + (8 if design_system.get("palette") else 0) + (5 if plan.get("graph") else 0)
        emotional = 76 + (12 if perception.get("primary") in ["desire", "warmth", "luxury", "editorial"] else 0)

        def clamp(value: float) -> float:
            return max(0.0, min(100.0, float(value)))

        return {
            "ctr_score": clamp(ctr),
            "luxury_score": clamp(luxury),
            "readability_score": clamp(readability),
            "brand_recall_score": clamp(brand_recall),
            "emotional_score": clamp(emotional),
            "analysis": {
                "visual_hierarchy": composition.get("eye_flow", []),
                "typography_map": typography,
                "attention_routing": composition.get("eye_flow", []),
                "risks": [
                    "Validate generated text readability manually after render.",
                    "Use real ad data to calibrate CTR score.",
                ],
            },
        }


class MockRenderProvider:
    def generate(self, prompt: str, context: dict | None = None) -> dict:
        del context
        return {
            "artifact_id": "mock_artifact",
            "artifact_type": "image",
            "mime_type": "image/png",
            "url": "https://placehold.co/1024x1024?text=Creative+Render",
            "provider_used": "mock",
            "prompt_used": prompt,
        }


class AdobeRenderProvider:
    def __init__(self) -> None:
        if settings.adobe_mode.lower() == "production":
            self.adapter = AdobeProductionAdapter(
                access_token=settings.adobe_api_key or "",
                client_id=settings.adobe_client_id or "",
            )
        else:
            self.adapter = AdobeMockAdapter()

    def generate(self, prompt: str, context: dict | None = None) -> dict:
        result = self.adapter.generate_visual(prompt, context or {})
        return {
            "artifact_id": result["adobe_asset_id"],
            "artifact_type": "image",
            "mime_type": "image/png",
            "url": result["image_url"],
            "provider_used": result["provider"],
            "prompt_used": prompt,
            "adobe_asset_id": result["adobe_asset_id"],
            "metadata": result.get("metadata", {}),
        }


class CanvaRenderProvider:
    def __init__(self) -> None:
        if settings.canva_mode.lower() == "production":
            self.adapter = CanvaProductionAdapter(access_token=settings.canva_access_token or "")
        else:
            self.adapter = CanvaMockAdapter()

    def generate(self, prompt: str, context: dict | None = None) -> dict:
        context = context or {}
        layout_payload = {
            "prompt": prompt,
            "offer": context.get("offer") or context.get("goal") or "Creative render",
            "brand": context.get("brand") or "Unknown brand",
            "brand_id": context.get("brand_id"),
            "template_id": context.get("template_id"),
        }
        result = self.adapter.create_layout(layout_payload)
        return {
            "artifact_id": result["canva_design_id"],
            "artifact_type": "layout",
            "mime_type": "image/png",
            "url": result["export_url"],
            "provider_used": result["provider"],
            "prompt_used": prompt,
            "canva_design_id": result["canva_design_id"],
            "metadata": result.get("metadata", {}),
        }


class AdobeCanvaRenderProvider:
    def __init__(self) -> None:
        self.adobe = AdobeRenderProvider()
        self.canva = CanvaRenderProvider()

    def generate(self, prompt: str, context: dict | None = None) -> dict:
        context = context or {}
        adobe_result = self.adobe.generate(prompt, context)
        canva_result = self.canva.generate(prompt, context)
        return {
            "artifact_id": canva_result.get("canva_design_id") or adobe_result["artifact_id"],
            "artifact_type": "image+layout",
            "mime_type": "image/png",
            "url": canva_result["url"],
            "provider_used": f"{adobe_result['provider_used']}+{canva_result['provider_used']}",
            "prompt_used": prompt,
            "adobe_asset_id": adobe_result.get("adobe_asset_id"),
            "canva_design_id": canva_result.get("canva_design_id"),
            "image_url": adobe_result["url"],
            "export_url": canva_result["url"],
            "metadata": {
                "adobe": adobe_result.get("metadata", {}),
                "canva": canva_result.get("metadata", {}),
            },
        }


class RenderProviderRegistry:
    def get(self, provider: str) -> MockRenderProvider | AdobeRenderProvider | CanvaRenderProvider | AdobeCanvaRenderProvider:
        normalized = provider.strip().lower()
        if normalized == "mock":
            return MockRenderProvider()
        if normalized in {"adobe", "adobe_real"}:
            return AdobeRenderProvider()
        if normalized in {"canva", "canva_real"}:
            return CanvaRenderProvider()
        if normalized in {"adobe+canva", "production", "real", "auto"}:
            return AdobeCanvaRenderProvider()
        return MockRenderProvider()