import asyncio
import hashlib

import httpx

from apps.api.core.config import settings
from packages.provider_adapters.base import ProviderError


class AdobeMockAdapter:
    def generate_visual(self, prompt: str, campaign_metadata: dict | None = None) -> dict:
        digest = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        return {
            "provider": "adobe_mock",
            "adobe_asset_id": f"adobe_mock_{digest}",
            "image_url": f"mock://adobe/{digest}.png",
            "metadata": {"mode": "mock", "prompt_hash": digest},
        }

    async def generate_visual_async(self, prompt: str, campaign_metadata: dict | None = None) -> dict:
        """Async passthrough for the mock adapter – no actual I/O to await."""
        return self.generate_visual(prompt, campaign_metadata)


class AdobeProductionAdapter:
    def __init__(
        self,
        access_token: str,
        client_id: str,
        base_url: str | None = None,
        poll_max_attempts: int | None = None,
        poll_interval_seconds: float | None = None,
    ):
        self.access_token = access_token
        self.client_id = client_id
        self.base_url = (base_url or settings.adobe_api_base_url).rstrip("/")
        # Allow callers (e.g. tests) to override poll behaviour without
        # mutating the global settings object (mirrors Canva adapter).
        self._poll_max_attempts = (
            poll_max_attempts
            if poll_max_attempts is not None
            else settings.adobe_poll_max_attempts
        )
        self._poll_interval_seconds = (
            poll_interval_seconds
            if poll_interval_seconds is not None
            else settings.adobe_poll_interval_seconds
        )

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": self.client_id,
            "Content-Type": "application/json",
        }

    def _map_error(self, response: httpx.Response) -> ProviderError:
        status = response.status_code
        if status in (401, 403):
            return ProviderError("adobe", "AUTH", retryable=False, message="Adobe authentication failed")
        if status == 429:
            return ProviderError("adobe", "RATE_LIMIT", retryable=True, message="Adobe rate limit exceeded")
        if 500 <= status <= 599:
            return ProviderError("adobe", "PROVIDER_DOWN", retryable=True, message="Adobe service unavailable")
        return ProviderError("adobe", "INVALID_PROMPT", retryable=False, message=f"Adobe request failed: {status}")

    def generate_visual(self, prompt: str, campaign_metadata: dict | None = None) -> dict:
        """Synchronous wrapper – runs the async implementation in a new event loop."""
        return asyncio.run(self.generate_visual_async(prompt, campaign_metadata))

    async def generate_visual_async(self, prompt: str, campaign_metadata: dict | None = None) -> dict:
        """Async implementation using httpx.AsyncClient to avoid blocking workers."""
        campaign_metadata = campaign_metadata or {}
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        payload = {
            "prompt": prompt,
            "numVariations": 1,
            "size": {"width": 1080, "height": 1350},
            "metadata": campaign_metadata,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/v3/images/generate-async",
                headers=self._headers(),
                json=payload,
            )
            if response.status_code >= 400:
                raise self._map_error(response)

            data = response.json()
            job_id = data.get("operationId") or data.get("operation_id") or data.get("job_id")
            if not job_id:
                outputs = data.get("outputs") or data.get("images") or []
                image_url = data.get("image_url") or (outputs[0].get("url") if outputs else None)
                if not image_url:
                    raise ProviderError("adobe", "PROVIDER_DOWN", retryable=True, message="Missing Adobe image URL")
                asset_id = data.get("asset_id") or data.get("assetId") or f"adobe_{prompt_hash}"
                return {
                    "provider": "adobe",
                    "adobe_asset_id": asset_id,
                    "image_url": image_url,
                    "metadata": {
                        "model": data.get("model", "unknown"),
                        "prompt_hash": prompt_hash,
                        "raw_response": data,
                    },
                }

            for _ in range(self._poll_max_attempts):
                poll = await client.get(
                    f"{self.base_url}/v3/images/operations/{job_id}",
                    headers=self._headers(),
                )
                if poll.status_code >= 400:
                    raise self._map_error(poll)
                poll_data = poll.json()
                status = str(poll_data.get("status", "")).lower()
                if status in {"done", "completed", "success"}:
                    outputs = poll_data.get("outputs") or poll_data.get("images") or []
                    image_url = poll_data.get("image_url") or (outputs[0].get("url") if outputs else None)
                    if not image_url:
                        raise ProviderError("adobe", "PROVIDER_DOWN", retryable=True, message="Adobe job done but no image")
                    asset_id = poll_data.get("asset_id") or poll_data.get("assetId") or f"adobe_{prompt_hash}"
                    return {
                        "provider": "adobe",
                        "adobe_asset_id": asset_id,
                        "image_url": image_url,
                        "metadata": {
                            "model": poll_data.get("model", "unknown"),
                            "prompt_hash": prompt_hash,
                            "raw_response": poll_data,
                        },
                    }
                if status in {"failed", "error"}:
                    raise ProviderError("adobe", "PROVIDER_DOWN", retryable=True, message="Adobe async job failed")
                # Non-blocking delay between polls.
                await asyncio.sleep(self._poll_interval_seconds)

        raise ProviderError("adobe", "PROVIDER_DOWN", retryable=True, message="Adobe async polling timeout")
