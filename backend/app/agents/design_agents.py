from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from .contracts import AgentEnvelope, AgentName, Lineage


INDUSTRY_PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "spa": {"video_type": "trust_relaxation_reel", "style": "soft luxury, before-after, calm voice"},
    "mỹ phẩm": {"video_type": "beauty_transformation_ads", "style": "macro texture, split before-after, product reveal"},
    "nha khoa": {"video_type": "trust_testimonial", "style": "clean clinic, smile proof, credibility"},
    "bất động sản": {"video_type": "cinematic_tour", "style": "wide angle, sunlight, premium lifestyle"},
    "giáo dục": {"video_type": "problem_solution_testimonial", "style": "clear pain point, parent/student proof"},
    "f&b": {"video_type": "sensory_food_reel", "style": "macro food, steam, crunch, appetite"},
    "thời trang": {"video_type": "lookbook_reel", "style": "street/editorial movement"},
    "sản phẩm số": {"video_type": "screen_demo", "style": "problem-solution, UI close-up"},
    "gym": {"video_type": "transformation_reel", "style": "energy, progress, proof"},
    "du lịch": {"video_type": "destination_teaser", "style": "cinematic travel montage"},
}


def _envelope(agent_name: AgentName, project_id: str, output: Dict[str, Any], reason: str, confidence: float, step: str) -> AgentEnvelope:
    return AgentEnvelope(
        agent_name=agent_name,
        project_id=project_id,
        output=output,
        decision_reason=reason,
        confidence_score=confidence,
        lineage=Lineage(step=step, artifact_id=str(uuid4())),
    )


def business_diagnosis(project_id: str, payload: Dict[str, Any]) -> AgentEnvelope:
    industry = payload.get("industry", "general")
    product = payload.get("product", "product")
    goal = payload.get("goal", "sales")
    output = {
        "creative_strategy": f"Position {product} for {goal} in {industry} with a clear pain-to-desire story.",
        "pain_point": payload.get("pain_point") or "Khách cần thấy lợi ích nhanh, rõ và đáng tin.",
        "selling_angle": payload.get("selling_angle") or "Biến nhu cầu hiện tại thành hành động mua ngay.",
        "visual_direction": "premium, clear hierarchy, strong product focus, readable CTA",
        "upsell_potential": 82,
    }
    return _envelope(AgentName.BUSINESS_DIAGNOSIS, project_id, output, "Input đủ để tạo strategy MVP.", 86, "business.diagnosed")


def industry_adaptation(project_id: str, payload: Dict[str, Any]) -> AgentEnvelope:
    industry = str(payload.get("industry", "general")).lower()
    playbook = INDUSTRY_PLAYBOOKS.get(industry, {"video_type": "short_video_ads", "style": "problem-solution-product-CTA"})
    output = {"industry": industry, "playbook": playbook, "recommended_video_type": playbook["video_type"]}
    return _envelope(AgentName.INDUSTRY_ADAPTATION, project_id, output, "Đã map ngành sang playbook phù hợp.", 84, "industry.adapted")


def image_design(project_id: str, payload: Dict[str, Any]) -> AgentEnvelope:
    product = payload.get("product", "sản phẩm")
    industry = payload.get("industry", "ngành")
    concepts: List[Dict[str, Any]] = []
    for idx, angle in enumerate(["Trust", "Conversion", "Viral"], start=1):
        concepts.append({
            "variant_index": idx,
            "concept_name": f"{angle} Poster for {product}",
            "headline": f"{product}: lựa chọn nổi bật cho {industry}",
            "cta": "Inbox để nhận tư vấn ngay",
            "layout_direction": "hero product center, benefit icons, strong CTA button",
            "visual_prompt": f"8K cinematic premium advertising poster for {product}, {industry}, {angle.lower()} angle, sharp product focus, luxury lighting, readable Vietnamese headline and CTA",
        })
    return _envelope(AgentName.IMAGE_DESIGN, project_id, {"concepts": concepts}, "Tạo 3 biến thể để test attention/trust/conversion.", 88, "image.concepts.generated")


def image_qa(project_id: str, image_variant: Dict[str, Any]) -> AgentEnvelope:
    prompt = image_variant.get("visual_prompt", "")
    base = 78 + min(len(prompt) // 80, 8)
    scores = {
        "attention_score": min(base + 5, 100),
        "trust_score": min(base, 100),
        "conversion_score": min(base + 3, 100),
        "brand_fit_score": min(base - 1, 100),
        "upsell_video_potential_score": min(base + 7, 100),
    }
    scores["VIDEO_UPSELL_READY"] = scores["upsell_video_potential_score"] >= 80
    return _envelope(AgentName.IMAGE_QA, project_id, {"scores": scores}, "Score dựa trên clarity, CTA, visual motion potential.", 82, "image.scored")


def upsell_opportunity(project_id: str, payload: Dict[str, Any]) -> AgentEnvelope:
    channel = payload.get("channel", "Facebook")
    product_type = payload.get("product_type", "physical")
    if channel.lower() in ["facebook", "tiktok"]:
        video_type = "15s video ads" if channel.lower() == "facebook" else "short reel"
    elif channel.lower() == "landing page":
        video_type = "hero video"
    elif product_type == "service":
        video_type = "trust/testimonial video"
    else:
        video_type = "product showcase video"
    output = {
        "upsell_reason": "Ảnh có thể tăng chuyển đổi khi thêm motion, hook và CTA động.",
        "video_type": video_type,
        "video_length": "15s",
        "estimated_business_value": "Tăng khả năng dừng lướt, tăng inbox và tạo cảm giác chuyên nghiệp hơn ảnh tĩnh.",
        "offer_message": "Bạn có muốn biến thiết kế này thành video quảng cáo 15 giây không?",
    }
    return _envelope(AgentName.UPSELL_OPPORTUNITY, project_id, output, "Kênh sử dụng phù hợp upsell video ngắn.", 89, "upsell.analyzed")


def video_concept(project_id: str, payload: Dict[str, Any]) -> AgentEnvelope:
    product = payload.get("product", "sản phẩm")
    output = {
        "video_hook": f"3 giây đầu cho thấy vấn đề trước khi {product} xuất hiện.",
        "story_angle": "before-after transformation with product reveal",
        "scene_list": ["Hook visual", "Problem", "Product reveal", "Benefit proof", "Offer + CTA"],
        "motion_style": "cinematic push-in, macro close-up, light sweep, smooth transitions",
        "voiceover_idea": "Một câu mở nỗi đau, một câu hứa hẹn lợi ích, một câu CTA.",
        "cta": "Inbox ngay để nhận tư vấn.",
    }
    return _envelope(AgentName.VIDEO_CONCEPT, project_id, output, "Concept giữ liên kết trực tiếp với ảnh đã chọn.", 87, "video.concept.generated")


def storyboard(project_id: str, payload: Dict[str, Any]) -> AgentEnvelope:
    scenes = [
        {"scene": 1, "role": "Hook visual", "duration": 3, "prompt": "Cinematic opening shot, strong problem visual, full frame, no crop."},
        {"scene": 2, "role": "Problem", "duration": 3, "prompt": "Show customer pain point clearly with emotional contrast."},
        {"scene": 3, "role": "Product reveal", "duration": 4, "prompt": "Premium product reveal, slow push-in, crisp reflections."},
        {"scene": 4, "role": "Benefit proof", "duration": 3, "prompt": "Show benefit icons and proof moment with trust cues."},
        {"scene": 5, "role": "Offer + CTA", "duration": 2, "prompt": "Clear offer screen, CTA button, readable text."},
    ]
    return _envelope(AgentName.STORYBOARD, project_id, {"scenes": scenes}, "Storyboard chuẩn 15s dùng được cho provider adapter.", 88, "storyboard.generated")


def offer(project_id: str, payload: Dict[str, Any]) -> AgentEnvelope:
    offers = [
        {"name": "Ảnh tĩnh → video 8s", "price": 99000, "best_for": "test nhanh"},
        {"name": "Ảnh tĩnh → video ads 15s", "price": 199000, "best_for": "chạy ads"},
        {"name": "Ảnh + 3 video biến thể", "price": 499000, "best_for": "A/B testing"},
        {"name": "Full campaign", "price": 999000, "best_for": "campaign launch"},
    ]
    return _envelope(AgentName.OFFER, project_id, {"offers": offers, "recommended": offers[1]}, "Gói 199k là entry offer dễ mua nhất.", 90, "offer.recommended")
