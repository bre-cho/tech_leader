from __future__ import annotations

import json
import logging
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass

_logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter as _PromCounter
except ImportError:  # pragma: no cover
    _PromCounter = None  # type: ignore[assignment]

_OAUTH_TOKEN_STORE_REDIS_FAILURE_TOTAL = (
    _PromCounter(
        "oauth_token_store_redis_failure_total",
        "Count of OAuth token store Redis read/write failures.",
        ("operation",),
    )
    if _PromCounter is not None
    else None
)


def _record_redis_failure(operation: str, exc: Exception) -> None:
    if _OAUTH_TOKEN_STORE_REDIS_FAILURE_TOTAL is not None:
        _OAUTH_TOKEN_STORE_REDIS_FAILURE_TOTAL.labels(operation=operation).inc()
    _logger.error("OAuth TokenStore Redis %s failure: %s", operation, exc, exc_info=True)


@dataclass(frozen=True)
class OAuthToken:
    access_token: str
    expires_in: int | None = None
    token_type: str = "Bearer"


class OAuthTokenRefreshError(RuntimeError):
    pass


class TokenStore:
    """Shared token store backed by Redis (preferred) with an os.environ fallback.

    In multi-process deployments (multiple Celery workers, API containers) every
    process shares the same Redis key so a token refreshed in one process is
    immediately visible to all others.  When Redis is unavailable the store
    falls back to os.environ so that single-process / test environments keep
    working without extra infrastructure.

    Usage::

        store = TokenStore()
        store.set("tiktok", token, expires_in=86400)
        access_token = store.get("tiktok")

    Redis key format: ``publish:token:{provider}`` (string, JSON payload).
    TTL is set to ``expires_in - 60`` seconds when ``expires_in`` is known.
    """

    # Redis key prefix — keep consistent across workers.
    _KEY_PREFIX = "publish:token:"
    # Minimum remaining TTL (seconds) before the key auto-expires.
    _TTL_SKEW = 60

    def __init__(self, redis_url: str | None = None) -> None:
        self._redis_url = redis_url or os.getenv("REDIS_URL") or _default_redis_url()
        self._redis = None  # lazy-connect

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, provider: str) -> str | None:
        """Return the stored access token for *provider*, or None."""
        try:
            raw = self._redis_get(self._key(provider))
            if raw:
                payload = json.loads(raw)
                return payload.get("access_token") or None
        except Exception as exc:  # noqa: BLE001
            _record_redis_failure("get", exc)
        # Env-var fallback (kept for single-process deployments / tests)
        return os.environ.get(f"{provider.upper()}_ACCESS_TOKEN") or None

    def set(self, provider: str, token: OAuthToken) -> None:
        """Persist *token* for *provider*.

        Writes to Redis (with TTL when expires_in is known) and falls back to
        updating os.environ so single-process code that reads env vars directly
        also sees the fresh token.
        """
        payload = json.dumps(
            {"access_token": token.access_token, "token_type": token.token_type}
        )
        ttl: int | None = None
        if token.expires_in is not None:
            ttl = max(1, token.expires_in - self._TTL_SKEW)
        try:
            self._redis_set(self._key(provider), payload, ttl=ttl)
        except Exception as exc:  # noqa: BLE001
            _record_redis_failure("set", exc)
        # Keep os.environ in sync for same-process callers in non-production
        # deployments (e.g. single-worker dev/test setups).  In production the
        # token is written to Redis only: writing to os.environ in a prefork
        # worker would only update one process's memory and cannot leak to
        # sibling processes via fork, so Redis is the canonical source.
        from app.core.production_gate import is_production_env  # noqa: PLC0415
        if not is_production_env():
            os.environ[f"{provider.upper()}_ACCESS_TOKEN"] = token.access_token

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _key(self, provider: str) -> str:
        return f"{self._KEY_PREFIX}{provider.lower()}"

    def _connect(self):
        import redis as _redis  # type: ignore[import]  # noqa: PLC0415

        if self._redis is None:
            self._redis = _redis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    def _redis_get(self, key: str) -> str | None:
        return self._connect().get(key)

    def _redis_set(self, key: str, value: str, *, ttl: int | None) -> None:
        r = self._connect()
        if ttl:
            r.setex(key, ttl, value)
        else:
            r.set(key, value)


def _default_redis_url() -> str:
    try:
        from app.core.config import settings  # noqa: PLC0415

        return settings.redis_url
    except Exception:
        return "redis://localhost:6379/0"


# Module-level singleton — import and use directly in workers.
token_store = TokenStore()


class OAuthTokenService:
    """Small OAuth refresh helper for live publish providers.

    Uses standard refresh_token grant. Providers can keep using static tokens in
    development, but production should configure refresh endpoints so expired
    tokens do not silently break publish jobs.
    """

    def refresh_from_env(self, prefix: str) -> OAuthToken | None:
        refresh_url = os.getenv(f"{prefix}_OAUTH_TOKEN_URL", "").strip()
        client_id = os.getenv(f"{prefix}_OAUTH_CLIENT_ID", "").strip()
        client_secret = os.getenv(f"{prefix}_OAUTH_CLIENT_SECRET", "").strip()
        refresh_token = os.getenv(f"{prefix}_OAUTH_REFRESH_TOKEN", "").strip()
        if not (refresh_url and client_id and client_secret and refresh_token):
            return None

        body = urllib.parse.urlencode(
            {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
            }
        ).encode()
        request = urllib.request.Request(
            refresh_url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:  # noqa: S310
                raw = json.loads(response.read())
        except Exception as exc:  # pragma: no cover - integration path
            raise OAuthTokenRefreshError(str(exc)) from exc

        token = str(raw.get("access_token") or "").strip()
        if not token:
            raise OAuthTokenRefreshError("OAuth refresh response missing access_token")
        return OAuthToken(
            access_token=token,
            expires_in=int(raw["expires_in"]) if raw.get("expires_in") is not None else None,
            token_type=str(raw.get("token_type") or "Bearer"),
        )

    @staticmethod
    def should_refresh(expires_at_epoch: float | None, *, skew_seconds: int = 300) -> bool:
        if expires_at_epoch is None:
            return False
        return time.time() + skew_seconds >= float(expires_at_epoch)

    def refresh_if_expiring(
        self,
        prefix: str,
        expires_at_epoch: float | None,
        *,
        skew_seconds: int = 300,
    ) -> OAuthToken | None:
        """Refresh the OAuth token for *prefix* if it will expire within *skew_seconds*.

        Returns the new :class:`OAuthToken` if a refresh was performed, or
        ``None`` if the current token is still valid or no refresh credentials
        are configured.

        Raises :class:`OAuthTokenRefreshError` on refresh failure so callers
        can transition the associated job to an error state rather than
        silently using an expired token.
        """
        if not self.should_refresh(expires_at_epoch, skew_seconds=skew_seconds):
            return None
        return self.refresh_from_env(prefix)
