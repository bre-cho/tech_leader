class SkillDistiller:
    def distill(self, context):
        best = context["best_concept"]
        req = context["request"]
        return {
            "skill_name": f"{req.industry.lower().replace(' ', '-')}-design-to-video-upsell",
            "reusable_pattern": "Business diagnosis → poster mechanism → scoring → video upsell → storyboard → offer",
            "trigger": f"industry={req.industry}; channel={req.channel}; goal={req.goal}",
            "winning_hook": best["headline"],
            "storyboard_pattern": "Hook→Problem→Product Reveal→Benefit Proof→Offer CTA",
        }
