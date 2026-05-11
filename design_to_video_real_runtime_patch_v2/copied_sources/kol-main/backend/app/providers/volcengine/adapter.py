from __future__ import annotations

import asyncio
from typing import Any

from app.providers.base import ProviderAdapter
from app.providers.config import provider_default_dry_run
from app.schemas.provider_schema import ProviderName, ProviderStatus

from .client import VolcengineArkClient
from .config import settings
from .message_utils import build_multimodal_user_message


class VolcengineProviderAdapter(ProviderAdapter):
    provider_name = ProviderName.volcengine

    def status(self) -> ProviderStatus:
        configured = bool(settings.VOLCENGINE_ARK_API_KEY)
        enabled = bool(settings.VOLCENGINE_ENABLED)
        return ProviderStatus(
            provider=self.provider_name,
            enabled=enabled,
            configured=configured,
            dry_run_default=provider_default_dry_run(),
            message="Volcengine Ark provider ready for chat and vision execution."
            if configured
            else "Volcengine Ark API key is missing.",
        )

    def build_payload(self, operation: str, input_data: dict[str, Any]) -> dict[str, Any]:
        if operation == "chat":
            return {
                "operation": operation,
                "model": input_data.get("model") or settings.VOLCENGINE_DEFAULT_TEXT_MODEL,
                "messages": input_data.get("messages", []),
                "temperature": input_data.get("temperature", 0.7),
                "max_tokens": input_data.get("max_tokens", 1024),
            }

        if operation == "vision_chat":
            return {
                "operation": operation,
                "model": input_data.get("model") or settings.VOLCENGINE_DEFAULT_TEXT_MODEL,
                "prompt": input_data.get("prompt"),
                "image_url": input_data.get("image_url"),
                "max_tokens": input_data.get("max_tokens", 1024),
            }

        return {"operation": operation, "input": input_data}

    def execute(self, operation: str, input_data: dict[str, Any], dry_run: bool = True):
        payload = self.build_payload(operation, input_data)
        if dry_run:
            return super().execute(operation=operation, input_data=input_data, dry_run=True)

        result = asyncio.run(self._execute_live(operation=operation, payload=payload))
        return self.build_execution_result(
            operation=operation,
            dry_run=False,
            payload=payload,
            accepted=True,
            result=result,
            message="Volcengine operation executed successfully.",
            external_job_id=result.get("id"),
        )

    async def _execute_live(self, *, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        client = VolcengineArkClient()
        if operation == "chat":
            return await client.chat_completion(
                messages=payload["messages"],
                model=payload.get("model"),
                temperature=payload.get("temperature", 0.7),
                max_tokens=payload.get("max_tokens", 1024),
            )

        if operation == "vision_chat":
            message = build_multimodal_user_message(
                prompt=str(payload["prompt"]),
                image_url=str(payload["image_url"]),
            )
            return await client.chat_completion(
                messages=[message],
                model=payload.get("model"),
                max_tokens=payload.get("max_tokens", 1024),
            )

        raise ValueError(f"Unsupported Volcengine operation: {operation}")
