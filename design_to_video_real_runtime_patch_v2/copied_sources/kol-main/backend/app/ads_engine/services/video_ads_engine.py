class VideoAdsEngine:
    def build_render_queue(self, variants, provider=None):
        queue = []
        for v in variants:
            payload = dict(v.get("render_payload", {}))
            if provider: payload["provider"] = provider
            payload["variant_id"] = v.get("variant_id")
            payload["video_prompt"] = v.get("video_prompt")
            payload["negative_prompt"] = v.get("negative_prompt")
            queue.append(payload)
        return queue

    def provider_recommendation(self, variant):
        fmt = variant.get("format"); concept = (variant.get("concept_name") or "").lower(); prompt = (variant.get("video_prompt") or "").lower()
        if fmt == "9:16" and ("demo" in concept or "lột xác" in concept): return "seedance2"
        if "high fashion" in concept or "cinematic" in prompt: return "veo"
        if "before" in prompt or "after" in prompt: return "runway"
        return "kling"
