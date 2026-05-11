from typing import Any

from .client import VolcengineArkClient, VolcengineProviderError
from .config import settings


class VolcengineCapabilityRouter:
    provider_name = "volcengine"

    def enabled(self) -> bool:
        return bool(settings.VOLCENGINE_ENABLED and settings.VOLCENGINE_ARK_API_KEY)

    def capabilities(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "enabled": self.enabled(),
            "auth_mode": "ark_api_key_no_login",
            "requires_console_login": False,
            "supports": {
                "chat": self.enabled(),
                "text_generation": self.enabled(),
                "vision_chat": self.enabled(),
                "video_generation": bool(self.enabled() and settings.VOLCENGINE_DEFAULT_VIDEO_MODEL),
            },
            "models": {
                "default_text": settings.VOLCENGINE_DEFAULT_TEXT_MODEL,
                "default_video": settings.VOLCENGINE_DEFAULT_VIDEO_MODEL,
            },
            "base_url": settings.VOLCENGINE_ARK_BASE_URL,
            "fallback_base_url": settings.VOLCENGINE_ARK_FALLBACK_BASE_URL,
        }

    async def run_chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled():
            raise VolcengineProviderError("Volcengine provider disabled or missing VOLCENGINE_ARK_API_KEY")

        client = VolcengineArkClient()
        try:
            return await client.chat_completion(**payload)
        except Exception:  # noqa: BLE001
            if settings.VOLCENGINE_ARK_FALLBACK_BASE_URL:
                fallback = VolcengineArkClient(base_url=settings.VOLCENGINE_ARK_FALLBACK_BASE_URL)
                return await fallback.chat_completion(**payload)
            raise
