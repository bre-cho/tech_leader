"""TikTok-specific publish provider.

Formats the job payload for the TikTok Content Posting API and delegates to
the HTTP layer.  Auth uses a user-access-token supplied via
``TIKTOK_ACCESS_TOKEN`` (or ``PUBLISH_PROVIDER_TOKEN``).

Upload URL is read from ``TIKTOK_UPLOAD_URL`` or ``PUBLISH_PROVIDER_URL``.

Token refresh:
  TikTok user access tokens expire after ~24 hours.  ``refresh_token()``
  implements the TikTok OAuth2 server-to-server refresh using
  ``TIKTOK_CLIENT_KEY``, ``TIKTOK_CLIENT_SECRET``, and
  ``TIKTOK_REFRESH_TOKEN``.  Call ``refresh_token()`` before a publish
  batch to ensure the access token is valid.
"""
from __future__ import annotations

import json as _json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.models.publish_job import PublishJob
from app.services.publish_providers.base import PublishProviderBase

_logger = logging.getLogger(__name__)

PUBLISH_MODE_REAL = "REAL"
PLATFORM = "tiktok"

# TikTok OAuth2 token refresh endpoint
_TIKTOK_TOKEN_REFRESH_URL = "https://open.tiktokapis.com/v2/oauth/token/"

_RETRIABLE_STATUS_CODES = frozenset(range(500, 600))
# TikTok API returns 429 for rate limit; treat as retriable with longer back-off.
_RETRIABLE_STATUS_CODES = _RETRIABLE_STATUS_CODES | frozenset({429})

# Supported privacy levels by the TikTok Content Posting API
_PRIVACY_LEVEL_MAP = {
    "public": "PUBLIC_TO_EVERYONE",
    "friends": "MUTUAL_FOLLOW_FRIENDS",
    "private": "SELF_ONLY",
}

# Rate limit: after a 429 response wait this many seconds before retrying
_RATE_LIMIT_BACKOFF_SECS = 60.0
_RATE_LIMIT_STATUS = 429


class ConfigurationError(Exception):
    """Raised when a required environment variable is missing."""


def refresh_tiktok_access_token() -> bool:
    """Refresh the TikTok user access token without instantiating a provider.

    This standalone function performs the OAuth2 server-to-server token
    refresh without requiring ``TIKTOK_UPLOAD_URL`` to be configured.  It is
    intended for use in periodic background workers (e.g. Celery beat tasks)
    where the publish endpoint is not needed.

    Reads ``TIKTOK_CLIENT_KEY``, ``TIKTOK_CLIENT_SECRET``, and
    ``TIKTOK_REFRESH_TOKEN`` from the environment.  On success the new
    access token is written back to ``TIKTOK_ACCESS_TOKEN`` (and the rotated
    refresh token, if any, to ``TIKTOK_REFRESH_TOKEN``) in the current
    process environment.

    Returns:
        ``True`` if the token was successfully refreshed.
        ``False`` if the OAuth credentials are absent (no-op for deployments
        that do not use TikTok publishing).

    Raises:
        :class:`ConfigurationError` if ``TIKTOK_TOKEN_REFRESH_URL`` is set to
        a non-allowlisted host.
        :class:`RuntimeError` on HTTP failure or missing ``access_token`` in
        the response.
    """
    client_key = os.environ.get("TIKTOK_CLIENT_KEY", "").strip()
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("TIKTOK_REFRESH_TOKEN", "").strip()

    if not (client_key and client_secret and refresh_token):
        return False

    token_url = os.environ.get("TIKTOK_TOKEN_REFRESH_URL", _TIKTOK_TOKEN_REFRESH_URL).strip()

    # Enforce that the token URL points to TikTok's official API domain so that
    # the TIKTOK_TOKEN_REFRESH_URL override cannot be used to redirect credentials
    # to an arbitrary server.  The only legitimate override is pointing to
    # a test stub under tiktokapis.com or localhost (integration tests only).
    _ALLOWED_TOKEN_HOSTS = frozenset({"open.tiktokapis.com"})
    try:
        _parsed_host = urllib.parse.urlparse(token_url).hostname or ""
    except Exception:
        _parsed_host = ""
    if _parsed_host not in _ALLOWED_TOKEN_HOSTS and not token_url.startswith(
        ("http://localhost", "http://127.")
    ):
        raise ConfigurationError(
            f"TIKTOK_TOKEN_REFRESH_URL must point to open.tiktokapis.com, got: {token_url!r}"
        )

    body = urllib.parse.urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode()

    req = urllib.request.Request(
        token_url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        # token_url is validated above to be open.tiktokapis.com or localhost (test only).
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 – URL is domain-validated above
            data: dict[str, Any] = _json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"TikTok token refresh failed with HTTP {exc.code}: {exc.read().decode(errors='replace')}"
        ) from exc

    new_access_token = (data.get("data") or data).get("access_token", "")
    if not new_access_token:
        raise RuntimeError(
            f"TikTok token refresh response did not contain access_token: {data}"
        )

    # Persist the new access token to the shared Redis store so every worker
    # process picks it up immediately.  os.environ is process-local and would
    # only benefit the single process that ran this refresh.
    from app.services.publish_providers.oauth_token_service import OAuthToken, token_store  # noqa: PLC0415
    token_store.set("tiktok", OAuthToken(access_token=new_access_token))

    # Update the refresh token in os.environ when the API rotated it.
    # The refresh token is long-lived, process-local storage is acceptable,
    # and it is read back from os.environ on the next refresh cycle in this
    # same process (or reloaded from environment at container restart).
    new_refresh_token = (data.get("data") or data).get("refresh_token", "")
    if new_refresh_token:
        os.environ["TIKTOK_REFRESH_TOKEN"] = new_refresh_token

    return True


class TikTokPublishProvider(PublishProviderBase):
    """TikTok Content Posting API adapter.

    Reads configuration from:
      - ``TIKTOK_UPLOAD_URL``    URL of the TikTok upload proxy / middleware
      - ``TIKTOK_ACCESS_TOKEN``  User access token
      - ``PUBLISH_PROVIDER_URL`` / ``PUBLISH_PROVIDER_TOKEN`` as fallbacks

    OAuth2 token refresh (optional):
      - ``TIKTOK_CLIENT_KEY``    App client key from TikTok developer portal
      - ``TIKTOK_CLIENT_SECRET`` App client secret from TikTok developer portal
      - ``TIKTOK_REFRESH_TOKEN`` Long-lived refresh token (valid ~365 days)
    """

    def __init__(self) -> None:
        self._url = (
            os.environ.get("TIKTOK_UPLOAD_URL", "").strip()
            or os.environ.get("PUBLISH_PROVIDER_URL", "").strip()
        )
        self._token = (
            os.environ.get("TIKTOK_ACCESS_TOKEN", "").strip()
            or os.environ.get("PUBLISH_PROVIDER_TOKEN", "").strip()
        )
        if not self._url:
            raise ConfigurationError(
                "TIKTOK_UPLOAD_URL (or PUBLISH_PROVIDER_URL) is required when "
                "publishing to TikTok.  Set it to your upload proxy endpoint."
            )

    def refresh_token(self) -> None:
        """Refresh the TikTok user access token via OAuth2 server-to-server flow.

        Reads ``TIKTOK_CLIENT_KEY``, ``TIKTOK_CLIENT_SECRET``, and
        ``TIKTOK_REFRESH_TOKEN`` from the environment.  On success the new
        access token is written back to ``TIKTOK_ACCESS_TOKEN`` in the current
        process environment so that subsequent ``execute()`` calls use it.

        If any of the required credentials are absent the method returns
        without raising so that providers without refresh capabilities can
        still function using the static access token.
        """
        refreshed = refresh_tiktok_access_token()
        if refreshed:
            # Keep the instance-level token in sync with the process environment.
            self._token = os.environ.get("TIKTOK_ACCESS_TOKEN", self._token)

    def execute(self, job: PublishJob) -> dict[str, Any]:
        """POST a TikTok-shaped payload and return the normalised response."""
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
                if exc.code == _RATE_LIMIT_STATUS:
                    # Rate-limited: use header-indicated wait or default backoff
                    retry_after = self._parse_retry_after(exc)
                    self._sleep(retry_after)
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
        raise RuntimeError("TikTokPublishProvider.execute() exhausted retries without exception")

    @staticmethod
    def _build_payload(job: PublishJob) -> dict[str, Any]:
        """Map the generic job payload to TikTok Content Posting API conventions."""
        payload: dict[str, Any] = job.payload or {}
        metadata: dict[str, Any] = payload.get("metadata") or {}
        raw_privacy = str(metadata.get("privacy_status") or "public").lower()
        privacy_level = _PRIVACY_LEVEL_MAP.get(raw_privacy, "PUBLIC_TO_EVERYONE")
        return {
            "job_id": job.id,
            "platform": PLATFORM,
            "publish_mode": job.publish_mode,
            # TikTok Content Posting API fields
            "post_info": {
                "title": str(payload.get("title_angle") or metadata.get("channel_name") or ""),
                "privacy_level": privacy_level,
                "disable_duet": bool(metadata.get("disable_duet", False)),
                "disable_comment": bool(metadata.get("disable_comment", False)),
                "disable_stitch": bool(metadata.get("disable_stitch", False)),
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": str(metadata.get("video_url") or ""),
            },
            "payload": payload,
        }

    def _do_request(self, body: bytes, headers: dict[str, str]) -> dict[str, Any]:
        req = urllib.request.Request(self._url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            return _json.loads(resp.read())

    @staticmethod
    def _parse_retry_after(exc: urllib.error.HTTPError) -> float:
        """Parse Retry-After header from a 429 response, falling back to default."""
        try:
            retry_after = exc.headers.get("Retry-After") or exc.headers.get("retry-after")
            if retry_after:
                return float(retry_after)
        except Exception as parse_exc:  # noqa: BLE001
            _logger.warning("TikTok retry-after parsing failed: %s", parse_exc)
        return _RATE_LIMIT_BACKOFF_SECS

    @staticmethod
    def _sleep(seconds: float) -> None:  # pragma: no cover
        time.sleep(seconds)
