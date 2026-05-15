from app.creative_infra_mvp.contracts import BusinessInput, DesignSystem, GraphEdge

class CreativeGraphEngine:
    def build(self, business: BusinessInput, ds: DesignSystem):
        edges = [
            GraphEdge(source="CloseUpFace", relation="increases", target="EmotionalAttention", weight=0.86, evidence="human face attracts first glance"),
            GraphEdge(source="ProductHero", relation="increases", target="PurchaseIntent", weight=0.82, evidence="clear product visibility improves decision confidence"),
            GraphEdge(source="ReadableTypography", relation="increases", target="CommercialReadability", weight=0.88, evidence="distance readability affects CTR"),
            GraphEdge(source="CTAContrast", relation="improves", target="ClickProbability", weight=0.80, evidence="high contrast CTA improves action clarity"),
        ]
        for color in ds.colors:
            if "gold" in color or "champagne" in color:
                edges.append(GraphEdge(source=color, relation="increases", target="LuxuryPerception", weight=0.84, evidence="gold/champagne cues premium perception"))
            if "white" in color or "ivory" in color:
                edges.append(GraphEdge(source=color, relation="increases", target="TrustPerception", weight=0.74, evidence="clean light colors signal hygiene and trust"))
        if "beauty" in business.industry.lower() or "cosmetic" in business.industry.lower():
            edges.append(GraphEdge(source="NaturalSkinTexture", relation="increases", target="BeautyTrust", weight=0.91, evidence="natural texture avoids plastic AI look"))
        return edges
