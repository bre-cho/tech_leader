from app.creative_infra_mvp.contracts import BusinessInput, DesignSystem, CanvasRegion, GraphEdge

class CreativePromptCompiler:
    def compile(self, business: BusinessInput, ds: DesignSystem, regions: list[CanvasRegion], edges: list[GraphEdge], agent_outputs):
        region_text = "\n".join([f"- {r.name}: {r.purpose}; rules: {', '.join(r.rules)}" for r in regions])
        graph_text = "\n".join([f"- {e.source} {e.relation} {e.target} (w={e.weight})" for e in edges[:8]])
        agents = "\n".join([f"- {a.agent}: {a.output}" for a in agent_outputs[:5]])

        prompt = f'''
AI-NATIVE CREATIVE BUSINESS INFRASTRUCTURE OUTPUT

Brand: {business.brand_name}
Industry: {business.industry}
Product: {business.product_name} ({business.product_type})
Audience: {business.audience}
Goal: {business.goal}
Channel: {business.channel}
Offer: {business.offer or "none"}

DESIGN SYSTEM:
Colors: {', '.join(ds.colors)}
Typography: {', '.join(ds.typography)}
Visual language: {', '.join(ds.visual_language)}
Composition rules: {', '.join(ds.composition_rules)}

AI-NATIVE DESIGN CANVAS:
{region_text}

CREATIVE INTELLIGENCE GRAPH:
{graph_text}

MULTI-AGENT WORKFORCE DECISIONS:
{agents}

COMMERCIAL RENDERING INSTRUCTIONS:
Create a premium commercial campaign visual with intentional attention routing:
emotional anchor → product hero → typography benefit → CTA.
The layout must be clean, realistic, conversion-focused, brand-consistent,
with strong material realism, typography-safe regions, natural lighting,
premium texture fidelity, social/billboard readability, and no distorted text.

POSTER-TO-VIDEO LOGIC:
The product should become the motion anchor.
Human gaze and body language should follow the product movement.
CTA appears only after product value is clear.
'''
        negative = "generic AI poster, unreadable text, distorted product, wrong logo, clutter, fake skin, plastic texture, broken anatomy, random particles, low-res"
        return prompt.strip(), negative
