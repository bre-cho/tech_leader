from app.agents.base import BaseAgent

class BusinessDiagnosisAgent(BaseAgent):
    name = "business-diagnosis-agent"
    required_inputs = ["request"]

    def execute(self, context):
        req = context["request"]
        industry = req.industry.lower()
        pain_map = {
            "spa": "khách cần niềm tin, cảm giác an toàn và kết quả nhìn thấy được",
            "mỹ phẩm": "khách cần thấy hiệu quả, texture sản phẩm và sự đáng tin của thương hiệu",
            "f&b": "khách cần kích thích vị giác, sự tươi ngon và lý do mua ngay",
            "bất động sản": "khách cần cảm giác sở hữu, uy tín và hình dung không gian sống",
            "giáo dục": "phụ huynh/học viên cần bằng chứng tiến bộ và uy tín chuyên môn",
        }
        pain = next((v for k, v in pain_map.items() if k in industry), "khách cần hiểu nhanh giá trị, tin tưởng và có lý do hành động")
        return {
            "industry": req.industry,
            "product": req.product,
            "audience": req.audience,
            "channel": req.channel,
            "goal": req.goal,
            "pain_point": pain,
            "selling_angle": f"Biến {req.product} thành giải pháp đáng tin cho {req.audience}",
            "creative_strategy": "high-trust conversion visual with clear product proof and emotional trigger",
            "visual_direction": f"{req.tone}; hero product/person focus; readable CTA; premium lighting",
            "upsell_potential": "high" if req.channel.lower() in ["facebook", "tiktok", "landing page"] else "medium",
        }
