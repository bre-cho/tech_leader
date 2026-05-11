import asyncio
import hashlib

import httpx

from apps.api.core.config import settings
from packages.provider_adapters.base import ProviderError


class CanvaMockAdapter:
    def create_layout(self, payload: dict) -> dict:
        raw = str(payload).encode()
        digest = hashlib.sha256(raw).hexdigest()[:16]
        return {
            "provider": "canva_mock",
            "canva_design_id": f"canva_mock_{digest}",
            "export_url": f"mock://canva/{digest}.pdf",
            "metadata": {"mode": "mock", "layout_hash": digest},
        }

    async def create_layout_async(self, payload: dict) -> dict:
        """Async passthrough for the mock adapter – no actual I/O to await."""
        return self.create_layout(payload)


class CanvaProductionAdapter:
    def __init__(
        self,
        access_token: str,
        base_url: str | None = None,
        poll_max_attempts: int | None = None,
        poll_interval_seconds: float | None = None,
    ):
        self.access_token = access_token
        self.base_url = (base_url or settings.canva_api_base_url).rstrip("/")
        # Allow callers (e.g. tests) to override poll behaviour without
        # mutating the global settings object.
        self._poll_max_attempts = (
            poll_max_attempts
            if poll_max_attempts is not None
            else settings.canva_poll_max_attempts
        )
        self._poll_interval_seconds = (
            poll_interval_seconds
            if poll_interval_seconds is not None
            else settings.canva_poll_interval_seconds
        )

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _map_error(self, response: httpx.Response) -> ProviderError:
        status = response.status_code
        if status in (401, 403):
            return ProviderError("canva", "AUTH", retryable=False, message="Canva authentication failed")
        if status == 429:
            return ProviderError("canva", "RATE_LIMIT", retryable=True, message="Canva rate limit exceeded")
        if 500 <= status <= 599:
            return ProviderError("canva", "PROVIDER_DOWN", retryable=True, message="Canva service unavailable")
        return ProviderError("canva", "INVALID_PROMPT", retryable=False, message=f"Canva request failed: {status}")

    def create_layout(self, payload: dict) -> dict:
        """Synchronous wrapper – runs the async implementation in a new event loop."""
        return asyncio.run(self.create_layout_async(payload))

    async def create_layout_async(self, payload: dict) -> dict:
        """Async implementation using httpx.AsyncClient to avoid blocking workers."""
        request_payload = {
            "template_id": payload.get("template_id"),
            "brand_template_id": payload.get("template_id"),
            "data": {
                "prompt": payload.get("prompt"),
                "offer": payload.get("offer"),
                "brand": payload.get("brand"),
            },
            "export": {
                "formats": ["png"],
                "sizes": ["4:5", "1:1", "9:16"],
            },
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/rest/v1/autofills",
                headers=self._headers(),
                json=request_payload,
            )
            if response.status_code >= 400:
                raise self._map_error(response)
            data = response.json()

        job_id = data.get("job_id") or data.get("id")
        if not job_id:
            raise ProviderError("canva", "PROVIDER_DOWN", retryable=True, message="Canva response missing job id")

        # Poll until the autofill job is complete.
        async with httpx.AsyncClient(timeout=30.0) as client:
            for _ in range(self._poll_max_attempts):
                poll_response = await client.get(
                    f"{self.base_url}/rest/v1/autofills/{job_id}", headers=self._headers()
                )
                if poll_response.status_code >= 400:
                    raise self._map_error(poll_response)
                poll_data = poll_response.json()

                status = str(poll_data.get("status", "")).lower()
                if status in {"failed", "error"}:
                    raise ProviderError("canva", "PROVIDER_DOWN", retryable=True, message="Canva autofill job failed")

                design_id = poll_data.get("design_id") or poll_data.get("design", {}).get("id")
                exports = poll_data.get("exports") or []
                export_url = poll_data.get("export_url") or (exports[0].get("url") if exports else None)

                if design_id and export_url:
                    return {
                        "provider": "canva",
                        "canva_design_id": design_id,
                        "export_url": export_url,
                        "metadata": {
                            "template_id": poll_data.get("template_id") or payload.get("template_id"),
                            "brand_id": poll_data.get("brand_id") or payload.get("brand_id"),
                            "raw_response": poll_data,
                        },
                    }

                # Non-blocking delay between polls.
                await asyncio.sleep(self._poll_interval_seconds)

        raise ProviderError("canva", "PROVIDER_DOWN", retryable=True, message="Canva autofill polling timeout")
