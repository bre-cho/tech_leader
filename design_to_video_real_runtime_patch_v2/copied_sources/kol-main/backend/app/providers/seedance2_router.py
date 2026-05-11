"""Seedance2 VideoProvider implementation for the low-level routing registry.

This module provides :class:`Seedance2Provider`, which implements the
:class:`~app.providers.video_router_base.VideoProvider` ABC used by
:func:`~app.providers.registry.build_provider_registry`.

For the production async adapter (used by the render pipeline via
:mod:`app.services.provider_router`) see
:mod:`app.providers.seedance2.adapter`.
"""
from __future__ import annotations

import os
from typing import Any, Dict

import requests

from .video_router_base import ProviderCapability, VideoProvider


class Seedance2Provider(VideoProvider):
    """VideoProvider implementation for the Seedance2 (BytePlus next-gen) API.

    Environment variables
    ---------------------
    SEEDANCE2_ENABLED
        Set to ``"true"`` to mark this provider as enabled.
    SEEDANCE2_API_KEY
        API key / Bearer token for the Seedance2 endpoint.
    SEEDANCE2_BASE_URL
        Base URL for the Seedance2 API gateway (no trailing slash).
    SEEDANCE2_DEFAULT_MODEL
        Default model name (default: ``"seedance-2.0"``).
    SEEDANCE2_CREATE_TASK_PATH
        Path for the create-task endpoint (default: ``"/video/generations"``).
    SEEDANCE2_GET_TASK_PATH_TEMPLATE
        Path template for the status endpoint; must contain ``{task_id}``
        (default: ``"/video/generations/{task_id}"``).
    """

    name = "seedance2"

    def __init__(self) -> None:
        self.enabled = os.getenv("SEEDANCE2_ENABLED", "false").lower() == "true"
        self.api_key = os.getenv("SEEDANCE2_API_KEY", "")
        self.base_url = os.getenv("SEEDANCE2_BASE_URL", "").rstrip("/")
        self.default_model = os.getenv("SEEDANCE2_DEFAULT_MODEL", "seedance-2.0")

    def capability(self) -> ProviderCapability:
        return ProviderCapability(
            name=self.name,
            modes={"text_to_video", "image_to_video"},
            enabled=self.enabled and bool(self.api_key) and bool(self.base_url),
            priority=5,          # higher priority than seedance (10)
            cost_score=0.60,
            latency_score=0.65,  # faster than seedance v1
            quality_score=0.80,
        )

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def healthcheck(self) -> bool:
        return self.capability().enabled

    def create_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        mode = payload.get("mode", "text_to_video")
        model = payload.get("provider_model") or self.default_model
        body: Dict[str, Any] = {
            "model": model,
            "prompt": payload["prompt"],
            "duration": payload.get("duration_seconds", 5),
            "aspect_ratio": payload.get("aspect_ratio", "16:9"),
        }
        if mode == "image_to_video" and payload.get("image_url"):
            body["image_url"] = str(payload["image_url"])
        if payload.get("negative_prompt"):
            body["negative_prompt"] = payload["negative_prompt"]

        endpoint = os.getenv("SEEDANCE2_CREATE_TASK_PATH", "/video/generations")
        resp = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        task_id = data.get("id") or data.get("job_id") or data.get("task_id")
        if not task_id:
            raise RuntimeError(f"Seedance2 task id missing: {data}")
        return {
            "provider": self.name,
            "external_task_id": task_id,
            "status": data.get("status", "submitted"),
            "raw": data,
        }

    def get_task(self, task_id: str) -> Dict[str, Any]:
        endpoint_tpl = os.getenv(
            "SEEDANCE2_GET_TASK_PATH_TEMPLATE", "/video/generations/{task_id}"
        )
        resp = requests.get(
            f"{self.base_url}{endpoint_tpl.format(task_id=task_id)}",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
