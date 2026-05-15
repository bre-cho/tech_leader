class Agent:
    name = "Agent"
    def report(self, output):
        return {"agent": self.name, "status": "completed", "output": output}

class CreativeDirectorAgent(Agent):
    name = "Creative Director Agent"
    def run(self, req, memory, graph_edges):
        return self.report({
            "direction": f"Build {req.campaign_name} as a business outcome campaign, not a single image.",
            "positioning": f"{req.product_name} should own a clear perception in {req.industry}: {req.goal}.",
            "must_use_memory": len(memory.get("campaign_evolution", [])) > 0,
        })

class BrandStrategistAgent(Agent):
    name = "Brand Strategist Agent"
    def run(self, req, memory):
        tone = memory.get("tone") or "premium, clear, trustworthy"
        return self.report({
            "tone": tone,
            "brand_dna": memory.get("brand_identity", {}),
            "positioning_rule": "preserve brand memory while testing new hooks",
        })

class DesignWorkforceAgent(Agent):
    name = "Design Workforce"
    def run(self, req, graph_edges):
        luxury = any("luxury" in e.target or "premium" in e.target for e in graph_edges)
        return self.report({
            "layout_system": "minimal editorial" if luxury else "clear conversion layout",
            "visual_hierarchy": ["attention hook", "product hero", "proof", "CTA"],
            "design_variation_rule": "change one dominant lever per variant for measurable learning",
        })

class VideoWorkforceAgent(Agent):
    name = "Video Workforce"
    def run(self, req):
        return self.report({
            "storyboard_pattern": "hook → product motion → benefit proof → CTA",
            "derivatives": ["TikTok 9:16", "Reel 9:16", "Landing hero 16:9", "Product loop 1:1"],
        })

class ConversionWorkforceAgent(Agent):
    name = "Conversion Workforce"
    def run(self, req):
        return self.report({
            "offer": req.offer or "low friction trial offer",
            "conversion_pattern": "outcome-first hook + product proof + direct CTA",
            "measurement": ["CTR", "CVR", "Revenue per impression", "Watch time rate"],
        })

class AnalyticsWorkforceAgent(Agent):
    name = "Analytics Workforce"
    def run(self):
        return self.report({
            "tracking": ["impressions", "clicks", "conversions", "revenue", "watch_time_rate"],
            "learning_rule": "update graph edges when a variant outperforms baseline",
        })

class MemoryWorkforceAgent(Agent):
    name = "Memory Workforce"
    def run(self, memory):
        return self.report({
            "recall_count": len(memory.get("campaign_evolution", [])),
            "memory_objects": ["BrandMemory", "CampaignMemory", "WinnerDNA", "OfferMemory", "ConversionMemory"],
        })
