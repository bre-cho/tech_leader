from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from typing import Any
from uuid import uuid4

import httpx


@dataclass
class RealImageVariant:
    variant_id: str
    provider: str
    asset_url: str | None
    prompt: str
    headline: str
    cta: str
    layout_direction: str
    trace_id: str
    raw_response: dict[str, Any]


class RealImageProviderBridge:
    """Bridge từ Design Studio MVP sang image/poster runtime thật của veo-main-7.

    Hỗ trợ 2 mode:
    1. POSTER_ENGINE_BASE_URL: gọi FastAPI poster-engine-backend đã copy từ veo-main-7.
    2. IMAGE_GENERATE_ENDPOINT: gọi Next route `/api/image/generate` đã copy từ veo-main-7.

    Production hard rule: không được trả placeholder nếu IMAGE_GENERATION_REQUIRED=true.
    """

    def __init__(self) -> None:
        self.mode = os.getenv("IMAGE_PROVIDER_MODE", "next_image_api").strip()
        self.poster_engine_base_url = os.getenv("POSTER_ENGINE_BASE_URL", "").rstrip("/")
        self.image_generate_endpoint = os.getenv("IMAGE_GENERATE_ENDPOINT", "").strip()
        self.required = os.getenv("IMAGE_GENERATION_REQUIRED", "true").lower() in {"1", "true", "yes", "on"}
        self.timeout_seconds = float(os.getenv("IMAGE_PROVIDER_TIMEOUT_SECONDS", "90"))

    async def generate_design_variants(self, *, diagnosis: dict[str, Any], count: int = 3) -> list[dict[str, Any]]:
        payload = self._build_payload(diagnosis=diagnosis, count=count)
        if self.mode == "poster_engine_backend":
            variants = await self._call_poster_engine(payload)
        else:
            variants = await self._call_next_image_api(payload)

        if self.required and not variants:
            raise RuntimeError("Real image generation returned no variants; production placeholder is blocked.")
        return [asdict(v) for v in variants]

    def _build_payload(self, *, diagnosis: dict[str, Any], count: int) -> dict[str, Any]:
        industry = diagnosis.get("industry") or diagnosis.get("business", {}).get("industry") or "general"
        product = diagnosis.get("product") or diagnosis.get("business", {}).get("product") or "product"
        goal = diagnosis.get("goal") or diagnosis.get("business", {}).get("goal") or "conversion"
        channel = diagnosis.get("channel") or diagnosis.get("business", {}).get("channel") or "facebook"
        visual_direction = diagnosis.get("visual_direction") or "cinematic premium commercial poster"
        selling_angle = diagnosis.get("selling_angle") or "clear benefit, trust, and conversion"
        return {
            "industry": industry,
            "product": product,
            "goal": goal,
            "channel": channel,
            "count": count,
            "creative_strategy": diagnosis.get("creative_strategy"),
            "selling_angle": selling_angle,
            "visual_direction": visual_direction,
            "quality": "8k ultra high resolution cinematic quality",
        }

    async def _call_next_image_api(self, payload: dict[str, Any]) -> list[RealImageVariant]:
        endpoint = self.image_generate_endpoint
        if not endpoint:
            raise RuntimeError("IMAGE_GENERATE_ENDPOINT is required for IMAGE_PROVIDER_MODE=next_image_api")
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
        return self._normalize_variants(data, default_provider="veo-main-next-image-api")

    async def _call_poster_engine(self, payload: dict[str, Any]) -> list[RealImageVariant]:
        if not self.poster_engine_base_url:
            raise RuntimeError("POSTER_ENGINE_BASE_URL is required for IMAGE_PROVIDER_MODE=poster_engine_backend")
        endpoint = f"{self.poster_engine_base_url}/projects"
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
        return self._normalize_variants(data, default_provider="veo-main-poster-engine-backend")

    def _normalize_variants(self, data: dict[str, Any], *, default_provider: str) -> list[RealImageVariant]:
        candidates = data.get("variants") or data.get("image_variants") or data.get("images") or []
        if isinstance(candidates, dict):
            candidates = [candidates]
        normalized: list[RealImageVariant] = []
        for item in candidates:
            if not isinstance(item, dict):
                continue
            asset_url = item.get("asset_url") or item.get("url") or item.get("image_url") or item.get("public_url")
            prompt = item.get("prompt") or item.get("visual_prompt") or item.get("description") or ""
            normalized.append(
                RealImageVariant(
                    variant_id=str(item.get("id") or item.get("variant_id") or uuid4()),
                    provider=str(item.get("provider") or default_provider),
                    asset_url=asset_url,
                    prompt=prompt,
                    headline=str(item.get("headline") or item.get("title") or ""),
                    cta=str(item.get("cta") or item.get("call_to_action") or ""),
                    layout_direction=str(item.get("layout_direction") or item.get("layout") or ""),
                    trace_id=str(item.get("trace_id") or data.get("trace_id") or uuid4()),
                    raw_response=item,
                )
            )
        return normalized
