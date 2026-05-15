from app.creative_infra_mvp.contracts import BusinessInput, CanvasRegion, DesignSystem

class DesignCanvasEngine:
    def plan_regions(self, business: BusinessInput, ds: DesignSystem):
        return [
            CanvasRegion(
                name="emotional_anchor",
                purpose="face / human emotion / primary hook",
                priority=1, x=0.05, y=0.08, width=0.42, height=0.46,
                rules=["must attract first glance", "do not cover eyes", "show emotion relevant to goal"]
            ),
            CanvasRegion(
                name="product_hero",
                purpose="product visibility and desire trigger",
                priority=2, x=0.50, y=0.18, width=0.38, height=0.42,
                rules=["label readable", "3/4 angle preferred", "material reflections must match lighting"]
            ),
            CanvasRegion(
                name="typography_zone",
                purpose="headline and benefit hierarchy",
                priority=3, x=0.08, y=0.58, width=0.82, height=0.18,
                rules=["large readable headline", "max 2 benefit lines", "avoid clutter"]
            ),
            CanvasRegion(
                name="cta_zone",
                purpose="conversion action",
                priority=4, x=0.52, y=0.80, width=0.36, height=0.11,
                rules=["high contrast", "clear offer", "tap-safe for mobile"]
            ),
            CanvasRegion(
                name="motion_reaction_zone",
                purpose="poster-to-video movement logic",
                priority=5, x=0.0, y=0.0, width=1.0, height=1.0,
                rules=["particles/mist/fabric/hair must react consistently", "movement should route attention to product"]
            ),
        ]
