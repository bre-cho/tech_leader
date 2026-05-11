"""Meta (Facebook / Instagram) publish provider.

Formats the job payload for the Meta Graph API (Instagram Content Publishing
or Facebook Pages API) and delegates to the HTTP layer.  Auth uses a
page/user access token via ``META_ACCESS_TOKEN`` (or ``PUBLISH_PROVIDER_TOKEN``).

Upload URL is read from ``META_UPLOAD_URL`` or ``PUBLISH_PROVIDER_URL``.
"""
from __future__ import annotations

import asyncio
import json as _json
import os
import time
import concurrent.futures
import urllib.error
import urllib.request
from typing import Any

from app.models.publish_job import PublishJob
from app.services.publish_providers.base import PublishProviderBase

PUBLISH_MODE_REAL = "REAL"
PLATFORM = "meta"

_RETRIABLE_STATUS_CODES = frozenset(range(500, 600))

# Default media type sent to the Graph API
_MEDIA_TYPE_MAP = {
    "short": "REELS",
    "talking_head": "REELS",
    "carousel": "CAROUSEL",
}


class ConfigurationError(Exception):
    """Raised when a required environment variable is missing."""


class MetaPublishProvider(PublishProviderBase):
    """Meta Graph API (Instagram/Facebook) publish adapter.

    Reads configuration from:
      - ``META_UPLOAD_URL``    URL of the Meta upload proxy / middleware
      - ``META_ACCESS_TOKEN``  Page / user access token
      - ``PUBLISH_PROVIDER_URL`` / ``PUBLISH_PROVIDER_TOKEN`` as fallbacks
    """

    def __init__(self) -> None:
        self._url = (
            os.environ.get("META_UPLOAD_URL", "").strip()
            or os.environ.get("PUBLISH_PROVIDER_URL", "").strip()
        )
        self._token = (
            os.environ.get("META_ACCESS_TOKEN", "").strip()
            or os.environ.get("PUBLISH_PROVIDER_TOKEN", "").strip()
        )
        if not self._url:
            raise ConfigurationError(
                "META_UPLOAD_URL (or PUBLISH_PROVIDER_URL) is required when "
                "publishing to Meta.  Set it to your upload proxy endpoint."
            )

    def execute(self, job: PublishJob) -> dict[str, Any]:
        """POST a Meta Graph API-shaped payload and return the normalised response."""
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
                }
            except urllib.error.HTTPError as exc:
                if exc.code not in _RETRIABLE_STATUS_CODES:
                    raise
                last_exc = exc
            except (urllib.error.URLError, OSError) as exc:
                last_exc = exc

            if attempt < max_retries:
                self._sleep(backoff_base * (2 ** attempt))

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("MetaPublishProvider.execute() exhausted retries without exception")

    @staticmethod
    def _build_payload(job: PublishJob) -> dict[str, Any]:
        """Map the generic job payload to Meta Graph API conventions."""
        payload: dict[str, Any] = job.payload or {}
        metadata: dict[str, Any] = payload.get("metadata") or {}
        fmt = str(payload.get("format") or "short").lower()
        media_type = _MEDIA_TYPE_MAP.get(fmt, "REELS")
        return {
            "job_id": job.id,
            "platform": PLATFORM,
            "publish_mode": job.publish_mode,
            # Meta Graph API fields
            "media_type": media_type,
            "caption": str(payload.get("title_angle") or metadata.get("channel_name") or ""),
            "video_url": str(metadata.get("video_url") or ""),
            "thumb_offset": int(metadata.get("thumb_offset_ms") or 0),
            "share_to_feed": bool(metadata.get("share_to_feed", True)),
            "payload": payload,
        }

    def _do_request(self, body: bytes, headers: dict[str, str]) -> dict[str, Any]:
        from app.core.config import settings  # noqa: PLC0415
        timeout = settings.provider_http_timeout_seconds
        req = urllib.request.Request(self._url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return _json.loads(resp.read())

    @staticmethod
    def _sleep(seconds: float) -> None:  # pragma: no cover
        """Sleep for *seconds*, respecting a running asyncio event loop.

        When called from a synchronous Celery worker there is no running loop,
        so ``time.sleep()`` is used directly.  When called from inside a
        running event loop (e.g. a FastAPI background task), ``loop.create_task``
        schedules an ``asyncio.sleep`` coroutine and a thread-safe ``Future``
        is used to block the calling thread until the coroutine completes.
        In practice all callers are synchronous Celery tasks, so this is a
        safety net rather than a common path.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None and loop.is_running():
            # Already inside a running event loop — schedule the async sleep
            # as a thread-safe future so we don't block the loop thread.
            future: concurrent.futures.Future[None] = concurrent.futures.Future()
            loop.call_soon_threadsafe(
                loop.create_task,
                _async_sleep_and_resolve(seconds, future),
            )
            future.result(timeout=seconds + 5)
        else:
            time.sleep(seconds)


async def _async_sleep_and_resolve(seconds: float, future: concurrent.futures.Future[None]) -> None:
    """Coroutine helper: sleep then resolve *future* so the synchronous caller unblocks."""
    try:
        await asyncio.sleep(seconds)
        future.set_result(None)
    except Exception as exc:  # noqa: BLE001
        if not future.done():
            future.set_exception(exc)
