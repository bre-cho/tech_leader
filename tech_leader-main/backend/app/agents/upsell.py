from app.agents.base import BaseAgent

class UpsellOpportunityAgent(BaseAgent):
    name = "upsell-opportunity-agent"
    required_inputs = ["request", "best_concept"]

    def execute(self, context):
        req = context["request"]
        channel = req.channel.lower()
        if "tiktok" in channel or "reel" in channel:
            video_type, length = "short-form reel ads", "15s"
        elif "landing" in channel:
            video_type, length = "hero website video", "8-12s"
        elif "facebook" in channel:
            video_type, length = "facebook conversion ads", "15s"
        else:
            video_type, length = "product/service showcase video", "15s"
        return {
            "video_upsell_ready": context["best_concept"]["score"]["video_upsell_ready"],
            "upsell_reason": f"Thiết kế '{context['best_concept']['headline']}' có thể chuyển thành {video_type} để tăng attention và conversion trên {req.channel}.",
            "video_type": video_type,
            "video_length": length,
            "estimated_business_value": "Tăng khả năng dừng cuộn, giải thích giá trị nhanh hơn ảnh tĩnh, tạo lý do mua gói video.",
            "offer_message": f"Bạn có muốn biến thiết kế này thành video quảng cáo {length} cho {req.product} không?",
        }
