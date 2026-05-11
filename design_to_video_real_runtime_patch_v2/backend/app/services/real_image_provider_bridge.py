from __future__ import annotations

import json
import os
from typing import Any, Dict, List
from urllib import error as url_error
from urllib import request as url_request


class RealImageProviderBridge:
    def __init__(self) -> None:
        self.app_env = os.getenv("APP_ENV", "development").lower()
        self.mode = os.getenv("IMAGE_PROVIDER_MODE", "next_image_api")
        self.required = os.getenv("IMAGE_GENERATION_REQUIRED", "true").lower() == "true"
        self.public_base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

    def _post_json(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = url_request.Request(endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with url_request.urlopen(req, timeout=25) as resp:  # nosec B310
            data = resp.read().decode("utf-8")
        return json.loads(data) if data else {}

    def _runtime_error(self, message: str) -> None:
        if self.app_env == "production" or self.required:
            raise RuntimeError(message)

    def _generate_with_poster_engine(self, project_id: str, trace_id: str, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        base_url = os.getenv("POSTER_ENGINE_BASE_URL", "").rstrip("/")
        if not base_url:
            self._runtime_error("POSTER_ENGINE_BASE_URL is required for poster_engine_backend mode")
            return []

        results: List[Dict[str, Any]] = []
        endpoint = f"{base_url}/generate"
        for concept in concepts:
            payload = {
                "project_id": project_id,
                "trace_id": trace_id,
                "prompt": concept.get("visual_prompt", ""),
                "headline": concept.get("headline", ""),
            }
            try:
                response = self._post_json(endpoint, payload)
                asset_url = response.get("asset_url")
                provider_job_id = response.get("job_id")
                if not asset_url:
                    self._runtime_error("poster_engine_backend returned no asset_url")
                    continue
                results.append({
                    **concept,
                    "asset_url": asset_url,
                    "provider": response.get("provider", "poster_engine_backend"),
                    "provider_job_id": provider_job_id,
                })
            except (url_error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                self._runtime_error(f"poster_engine_backend call failed: {exc}")

        return results

    def _generate_with_next_image_api(self, project_id: str, trace_id: str, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        endpoint = os.getenv("IMAGE_GENERATE_ENDPOINT", "").strip()
        if not endpoint:
            self._runtime_error("IMAGE_GENERATE_ENDPOINT is required for next_image_api mode")
            return []

        results: List[Dict[str, Any]] = []
        for concept in concepts:
            payload = {
                "project_id": project_id,
                "trace_id": trace_id,
                "prompt": concept.get("visual_prompt", ""),
            }
            try:
                response = self._post_json(endpoint, payload)
                asset_url = response.get("asset_url")
                if not asset_url:
                    self._runtime_error("next_image_api returned no asset_url")
                    continue
                results.append({
                    **concept,
                    "asset_url": asset_url,
                    "provider": response.get("provider", "next_image_api"),
                    "provider_job_id": response.get("job_id"),
                })
            except (url_error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                self._runtime_error(f"next_image_api call failed: {exc}")

        return results

    def _fallback_local_assets(self, project_id: str, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                **concept,
                "asset_url": f"{self.public_base_url}/artifacts/images/{project_id}-{concept.get('variant_index', 0)}.png",
                "provider": "local_stub",
                "provider_job_id": None,
            }
            for concept in concepts
        ]

    def generate_variants(self, project_id: str, trace_id: str, concepts: List[Dict[str, Any]], payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not concepts:
            return []

        if self.mode == "poster_engine_backend":
            variants = self._generate_with_poster_engine(project_id, trace_id, concepts)
        elif self.mode == "next_image_api":
            variants = self._generate_with_next_image_api(project_id, trace_id, concepts)
        else:
            self._runtime_error(f"Unsupported IMAGE_PROVIDER_MODE: {self.mode}")
            variants = []

        if variants:
            return variants

        if self.app_env == "production":
            raise RuntimeError("Image generation failed in production and fallback is not allowed")

        return self._fallback_local_assets(project_id, concepts)
