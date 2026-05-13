from app.agents.base import BaseAgent

class StoryboardAgent(BaseAgent):
    name = "storyboard-agent"
    required_inputs = ["request", "video_concept"]

    def execute(self, context):
        req = context["request"]
        vc = context["video_concept"]
        scene_specs = [
            (1, "Hook visual", "Dừng cuộn bằng hình ảnh mạnh nhất", "fast push-in, premium light sweep"),
            (2, "Problem", f"Nêu nỗi đau của {req.audience}", "subtle close-up, emotional pacing"),
            (3, "Product reveal", f"Reveal {req.product}", "cinematic orbit, crisp product details"),
            (4, "Benefit proof", "Cho thấy kết quả/lợi ích rõ ràng", "before-after / proof overlay motion"),
            (5, "Offer CTA", vc["cta"], "end card, readable CTA, brand lockup"),
        ]
        scenes = []
        for idx, title, objective, camera in scene_specs:
            prompt = (
                f"Scene {idx}: {title}. Objective: {objective}. Brand/product: {req.brand_name or req.product}. "
                f"Industry: {req.industry}. Audience: {req.audience}. Visual style: {vc['motion_style']}. "
                f"Camera: {camera}. Full frame composition, no crop, cinematic commercial lighting, premium finish."
            )
            scenes.append({
                "scene_id": f"SC-{idx:02d}",
                "title": title,
                "duration_sec": 3 if idx < 5 else 4,
                "objective": objective,
                "camera_motion": camera,
                "visual_prompt": prompt,
                "voiceover": vc["voiceover_idea"] if idx in [1, 2] else "",
                "provider_payload_ready": True,
            })
        return scenes

    def execute_full(self, context):
        base = self.execute(context)
        return {
            "trust_variant": base,
            "viral_variant": [{**s, "camera_motion": s["camera_motion"] + ", faster social pacing"} for s in base],
            "conversion_variant": [{**s, "objective": s["objective"] + " + conversion proof"} for s in base],
        }
