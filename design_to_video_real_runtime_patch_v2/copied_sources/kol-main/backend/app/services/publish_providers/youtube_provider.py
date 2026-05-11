"""YouTube-specific publish provider.

P13 supports two execution modes:
  1. Native YouTube Data API v3 resumable upload when YOUTUBE_NATIVE_ENABLED=true.
  2. Existing upload proxy / middleware fallback for non-native deployments.

Native mode includes OAuth refresh, resumable upload, status polling, thumbnail
upload, schedule/visibility mapping and compliance preflight.
"""
from __future__ import annotations

import json as _json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Any

from app.models.publish_job import PublishJob
from app.services.publish_providers.base import PublishProviderBase
from app.services.publish_providers.youtube_compliance import run_youtube_compliance_preflight
from app.services.publish_providers.youtube_native_client import YouTubeNativeClient

_logger = logging.getLogger(__name__)

PUBLISH_MODE_REAL = "REAL"
PLATFORM = "youtube"

_RETRIABLE_STATUS_CODES = frozenset(range(500, 600)) | frozenset({429})
_DEFAULT_CATEGORY_ID = "22"
_RATE_LIMIT_BACKOFF_SECS = 60.0
_RATE_LIMIT_STATUS = 429


class ConfigurationError(Exception):
    """Raised when a required environment variable is missing."""


def _env_true(name: str) -> bool:
    return os.getenv(name, "").lower() in {"1", "true", "yes", "on"}


class YouTubePublishProvider(PublishProviderBase):
    """YouTube publish adapter with native API support."""

    def __init__(self) -> None:
        self._native_enabled = _env_true("YOUTUBE_NATIVE_ENABLED")
        self._url = (
            os.environ.get("YOUTUBE_UPLOAD_URL", "").strip()
            or os.environ.get("PUBLISH_PROVIDER_URL", "").strip()
        )
        self._token = (
            os.environ.get("YOUTUBE_API_TOKEN", "").strip()
            or os.environ.get("PUBLISH_PROVIDER_TOKEN", "").strip()
        )
        if not self._native_enabled and not self._url:
            raise ConfigurationError(
                "Set YOUTUBE_NATIVE_ENABLED=true for native YouTube API publishing, "
                "or configure YOUTUBE_UPLOAD_URL/PUBLISH_PROVIDER_URL for proxy mode."
            )

    def execute(self, job: PublishJob) -> dict[str, Any]:
        payload = job.payload or job.request_payload or {}
        compliance = run_youtube_compliance_preflight(payload)
        if not compliance.ok:
            raise ValueError({"provider": PLATFORM, "compliance_errors": compliance.errors})

        if self._native_enabled:
            return self._execute_native(job, payload, compliance.warnings)
        return self._execute_proxy(job, compliance.warnings)

    def _execute_native(self, job: PublishJob, payload: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
        built = self._build_payload(job)
        metadata = payload.get("metadata") or {}
        client = YouTubeNativeClient(timeout_seconds=int(os.getenv("YOUTUBE_NATIVE_TIMEOUT_SECONDS", "60")))
        raw = client.publish_video(
            video_source=str(payload.get("final_video_url") or payload.get("video_url") or metadata.get("final_video_url")),
            snippet=built["snippet"],
            status=built["status"],
            thumbnail_source=(payload.get("thumbnail_url") or metadata.get("thumbnail_url")),
            poll=_env_true("YOUTUBE_POLL_AFTER_UPLOAD"),
        )
        return {
            "ok": bool(raw.get("ok", True)),
            "mode": "NATIVE_YOUTUBE_API",
            "platform": PLATFORM,
            "provider_publish_id": raw.get("provider_publish_id") or job.id,
            "raw": raw,
            "compliance_warnings": warnings,
        }

    def _execute_proxy(self, job: PublishJob, warnings: list[str]) -> dict[str, Any]:
        from app.core.config import settings

        max_retries: int = settings.provider_max_retries
        backoff_base: float = float(settings.provider_retry_base_seconds)
        body = _json.dumps(self._build_payload(job)).encode()
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                raw = self._do_request(body, headers)
                return {
                    "ok": bool(raw.get("ok", True)),
                    "mode": PUBLISH_MODE_REAL,
                    "platform": PLATFORM,
                    "provider_publish_id": raw.get("provider_publish_id") or raw.get("id") or job.id,
                    "raw": raw,
                    "compliance_warnings": warnings,
                }
            except urllib.error.HTTPError as exc:
                if exc.code == _RATE_LIMIT_STATUS:
                    self._sleep(self._parse_retry_after(exc))
                    last_exc = exc
                elif exc.code not in _RETRIABLE_STATUS_CODES:
                    raise
                else:
                    last_exc = exc
            except (urllib.error.URLError, OSError) as exc:
                last_exc = exc
            if attempt < max_retries:
                self._sleep(backoff_base * (2 ** attempt))
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("YouTubePublishProvider.execute() exhausted retries without exception")

    @staticmethod
    def _build_payload(job: PublishJob) -> dict[str, Any]:
        payload: dict[str, Any] = job.payload or job.request_payload or {}
        metadata: dict[str, Any] = payload.get("metadata") or {}
        seo: dict[str, Any] = payload.get("youtube_seo") or {}
        scheduled_for = metadata.get("scheduled_for") or payload.get("scheduled_for")
        privacy_status = str(metadata.get("privacy_status") or payload.get("privacy_status") or "public")
        status = {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": bool(metadata.get("made_for_kids", payload.get("made_for_kids", False))),
        }
        if scheduled_for:
            status["publishAt"] = str(scheduled_for)
            # YouTube requires scheduled videos to be uploaded private first.
            status["privacyStatus"] = "private"

        return {
            "job_id": job.id,
            "platform": PLATFORM,
            "publish_mode": job.publish_mode,
            "snippet": {
                "title": str(seo.get("title") or payload.get("title_angle") or metadata.get("channel_name") or payload.get("title") or "Untitled")[:100],
                "description": str(seo.get("description") or payload.get("content_goal") or metadata.get("description") or "")[:5000],
                "categoryId": str(metadata.get("category_id") or _DEFAULT_CATEGORY_ID),
                "tags": seo.get("tags") or metadata.get("tags") or [],
            },
            "status": status,
            "payload": payload,
            "seo_package": seo,
            "post_publish_actions": {
                "pin_comment": seo.get("pinned_comment"),
                "thumbnail_brief": seo.get("thumbnail_brief"),
            },
        }

    def _do_request(self, body: bytes, headers: dict[str, str]) -> dict[str, Any]:
        req = urllib.request.Request(self._url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            return _json.loads(resp.read())

    @staticmethod
    def _parse_retry_after(exc: urllib.error.HTTPError) -> float:
        try:
            retry_after = exc.headers.get("Retry-After") or exc.headers.get("retry-after")
            if retry_after:
                return float(retry_after)
        except Exception as parse_exc:  # noqa: BLE001
            _logger.warning("YouTube retry-after parsing failed: %s", parse_exc)
        return _RATE_LIMIT_BACKOFF_SECS

    def refresh_token(self) -> None:
        """Refresh the YouTube OAuth2 access token.

        Called by the publish scheduler before a batch when the token may be
        close to expiry.  Persists the new token to the shared :data:`token_store`
        (Redis) so every worker process sees the update immediately.

        No-ops silently when native mode is disabled (proxy mode uses static
        API tokens that do not require rotation) or when the required OAuth2
        credentials are not configured.
        """
        if not self._native_enabled:
            return
        try:
            from app.services.publish_providers.oauth_token_service import OAuthToken, token_store  # noqa: PLC0415

            client = YouTubeNativeClient()
            new_token = client.refresh_access_token()
            # Write to the shared store (Redis-backed) so all worker processes
            # pick up the new token.  os.environ is process-local and would only
            # benefit this single process.
            token_store.set("youtube", OAuthToken(access_token=new_token))
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "YouTubePublishProvider.refresh_token: token refresh failed (non-fatal): %s", exc
            )  # Non-fatal: rotation failure must not block the current publish batch

    @staticmethod
    def _sleep(seconds: float) -> None:  # pragma: no cover
        time.sleep(seconds)
