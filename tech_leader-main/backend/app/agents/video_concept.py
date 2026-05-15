from app.agents.base import BaseAgent

class VideoConceptAgent(BaseAgent):
    name = "video-concept-agent"
    required_inputs = ["request", "best_concept", "upsell_analysis"]

    def execute(self, context):
        req = context["request"]
        best = context["best_concept"]
        return {
            "hook": best["headline"],
            "story_angle": f"Từ vấn đề của {req.audience} đến giải pháp {req.product}",
            "motion_style": "cinematic product reveal, smooth push-in, premium transitions, readable CTA end card",
            "voiceover_idea": f"Bạn đang tìm {req.product} đáng tin? Đây là lựa chọn dành cho {req.audience}.",
            "cta": best["cta"],
            "provider_targets": ["Veo", "Runway", "Kling", "Seedance"],
        }
