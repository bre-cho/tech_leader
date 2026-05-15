from __future__ import annotations

from app.core.contracts import BusinessInput, VisualDecision
from app.intelligence.attention_routing import AttentionRoutingEngine
from app.intelligence.typography_engine import TypographyHierarchyEngine
from app.intelligence.product_hero import ProductHeroEngine
from app.intelligence.environment_reaction import EnvironmentReactionEngine
from app.intelligence.commercial_psychology import CommercialPsychologyEngine
from app.intelligence.billboard_print import BillboardPrintEngine
from app.intelligence.category_engine import CategoryCommercialEngine


class CommercialVisualReasoner:
    def __init__(self):
        self.category = CategoryCommercialEngine()
        self.attention = AttentionRoutingEngine()
        self.typography = TypographyHierarchyEngine()
        self.product = ProductHeroEngine()
        self.environment = EnvironmentReactionEngine()
        self.psychology = CommercialPsychologyEngine()
        self.printing = BillboardPrintEngine()

    def reason(self, business: BusinessInput, export_targets):
        category_profile = self.category.analyze(business.industry, business.product_type)
        attention = self.attention.build_route(category_profile, business.goal.value)
        typography = self.typography.plan(business.channel.value, category_profile["category"], business.brand_tone or "")
        product = self.product.plan(business.product_type, category_profile["category"])
        environment = self.environment.plan(category_profile["category"], category_profile["emotion_targets"])
        psychology = self.psychology.map(category_profile)
        print_plan = self.printing.plan(export_targets)

        return VisualDecision(
            attention_route=attention["route"],
            dopamine_triggers=attention["dopamine_triggers"],
            trust_triggers=category_profile["trust_rules"],
            conversion_triggers=attention["conversion_triggers"],
            typography_plan=typography,
            product_hero_plan=product,
            environment_reaction_plan=environment,
            commercial_psychology=psychology,
            print_export_plan=print_plan,
        )
