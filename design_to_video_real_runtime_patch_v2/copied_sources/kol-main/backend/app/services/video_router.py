import os
from typing import Any, Dict, List

from app.providers.registry import build_provider_registry


class NoProviderAvailable(RuntimeError):
    pass


class MultiProviderVideoRouter:
    def __init__(self) -> None:
        self.providers = build_provider_registry()
        self.max_retries = int(os.getenv("VIDEO_ROUTER_MAX_RETRIES", "2"))

    def _score(self, provider_name: str, mode: str) -> float:
        provider = self.providers[provider_name]
        cap = provider.capability()
        if not cap.enabled or mode not in cap.modes or not provider.healthcheck():
            return -1
        return (cap.quality_score * 0.5) + (cap.latency_score * 0.25) + (cap.cost_score * 0.25) - (cap.priority / 1000)

    def select_chain(self, mode: str, provider_hint: str | None = None) -> List[str]:
        configured = [x.strip() for x in os.getenv("VIDEO_ROUTER_FALLBACK_ORDER", "seedance,runway,kling").split(",") if x.strip()]
        candidates = [p for p in configured if p in self.providers]
        if provider_hint and provider_hint in self.providers:
            candidates = [provider_hint] + [p for p in candidates if p != provider_hint]
        candidates = [p for p in candidates if self._score(p, mode) >= 0]
        return sorted(candidates, key=lambda p: self._score(p, mode), reverse=True)

    def create_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        mode = payload["mode"]
        chain = self.select_chain(mode, payload.get("provider_hint"))
        if not chain:
            raise NoProviderAvailable(f"No provider available for mode={mode}")

        errors: List[str] = []
        for provider_name in chain:
            provider = self.providers[provider_name]
            for attempt in range(self.max_retries + 1):
                try:
                    task = provider.create_task(payload)
                    return {
                        "selected_provider": provider_name,
                        "mode": mode,
                        "task": task,
                        "fallback_chain": chain,
                    }
                except Exception as exc:
                    errors.append(f"{provider_name}[attempt={attempt}]: {exc}")
                    if attempt >= self.max_retries:
                        break
        raise NoProviderAvailable("All providers failed: " + " | ".join(errors))

    def health(self) -> Dict[str, Any]:
        data = {}
        for name, provider in self.providers.items():
            cap = provider.capability()
            data[name] = {
                "enabled": cap.enabled,
                "healthy": provider.healthcheck(),
                "modes": sorted(cap.modes),
                "score_text_to_video": self._score(name, "text_to_video"),
                "score_image_to_video": self._score(name, "image_to_video"),
            }
        return data
