from __future__ import annotations


class CapabilityRouter:
    def route(self, business, provider: str):
        capabilities = ["commercial_reasoning", "prompt_compile", "visual_generation", "qa", "memory"]
        if business.channel.value == "billboard":
            capabilities.append("print_readiness")
        if business.industry.lower() in {"beauty", "cosmetics", "fashion"}:
            capabilities.append("beauty_fashion_perception")
        return {"provider": provider, "capabilities": capabilities}
