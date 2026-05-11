import time
from typing import Any

import httpx

from .config import settings


class VolcengineProviderError(RuntimeError):
    pass


class VolcengineArkClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        self.api_key = api_key or settings.VOLCENGINE_ARK_API_KEY
        self.base_url = (base_url or settings.VOLCENGINE_ARK_BASE_URL).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.VOLCENGINE_TIMEOUT_SECONDS
        self.max_retries = max_retries or settings.VOLCENGINE_MAX_RETRIES

        if not self.api_key:
            raise VolcengineProviderError("VOLCENGINE_ARK_API_KEY is missing")

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        last_error: Exception | None = None

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for attempt in range(self.max_retries + 1):
                try:
                    response = await client.request(method, url, headers=self.headers, json=payload)
                    if response.status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                        await self._sleep(attempt)
                        continue
                    response.raise_for_status()
                    return response.json()
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
                    if attempt >= self.max_retries:
                        break
                    await self._sleep(attempt)

        raise VolcengineProviderError(f"Ark request failed: {last_error}") from last_error

    async def _sleep(self, attempt: int) -> None:
        import asyncio

        await asyncio.sleep(min(2 ** attempt, 8))

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **extra: Any,
    ) -> dict[str, Any]:
        payload = {
            "model": model or settings.VOLCENGINE_DEFAULT_TEXT_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **extra,
        }
        return await self._request("POST", "/chat/completions", payload)

    async def healthcheck(self) -> dict[str, Any]:
        model = settings.VOLCENGINE_HEALTH_MODEL or settings.VOLCENGINE_DEFAULT_TEXT_MODEL
        started = time.time()
        result = await self.chat_completion(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            temperature=0,
            max_tokens=8,
        )
        return {
            "ok": True,
            "provider": "volcengine",
            "mode": "ark_api_key_no_login",
            "base_url": self.base_url,
            "model": model,
            "latency_ms": int((time.time() - started) * 1000),
            "response_id": result.get("id"),
        }


async def build_ark_client_with_region_fallback() -> VolcengineArkClient:
    return VolcengineArkClient()
