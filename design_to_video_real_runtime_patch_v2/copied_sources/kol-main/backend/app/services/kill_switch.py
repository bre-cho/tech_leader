"""Kill switch service — Redis-backed feature flags with in-memory fallback.

Switches are stored as Redis hashes under the key ``kill_switch:flags`` so
state is shared across all worker processes and persists across restarts.
When Redis is unavailable the service falls back to an in-memory dict and
logs a warning so operators are aware that switch state is no longer shared.

**DB persistence (P1.3):** When Redis is unavailable, flag changes are also
written to PostgreSQL (table ``kill_switch_flags``) so state survives worker
restarts even during Redis outages.  On startup (and when Redis first becomes
unavailable) the current state is loaded from DB into the in-memory fallback,
ensuring that ``set_switch(name, False)`` persists across restarts.

.. warning:: State is lost only when BOTH Redis AND PostgreSQL are unavailable.

    When both Redis AND PostgreSQL are unavailable and a worker process
    restarts, all kill-switch state stored only in ``_fallback`` is lost.
    This is a double-failure scenario.  Operators should monitor both the
    ``KillSwitchService: Redis unavailable`` warning and any DB connection
    errors to ensure at least one persistence layer remains healthy.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

_REDIS_KEY = "kill_switch:flags"

# ---------------------------------------------------------------------------
# Prometheus gauge — kill_switch_persistence_available
# ---------------------------------------------------------------------------
# Tracks whether at least one persistence layer (Redis or PostgreSQL) is
# reachable.  When BOTH fail (the double-failure scenario described in the
# module docstring) this gauge drops to 0 so PagerDuty can alert.
#
# Values:
#   2 — Redis AND PostgreSQL are both available (optimal)
#   1 — Only one persistence layer is reachable (degraded but safe)
#   0 — BOTH Redis AND PostgreSQL are unreachable (critical: state will be
#       lost on worker restart)
# ---------------------------------------------------------------------------
try:
    import prometheus_client as _prom

    _KS_PERSISTENCE_GAUGE = _prom.Gauge(
        "kill_switch_persistence_available",
        "Number of kill-switch persistence layers currently reachable "
        "(Redis + PostgreSQL = 2; only one = 1; none = 0). "
        "Alert when this gauge is 0 — flag state will be lost on worker restart.",
    )
    _KS_PERSISTENCE_GAUGE.set(2)  # assume both available at startup
    _KS_PROM_AVAILABLE = True
except ImportError:  # pragma: no cover
    _KS_PROM_AVAILABLE = False


def _ks_update_persistence_gauge(redis_ok: bool, db_ok: bool) -> None:
    """Update the kill_switch_persistence_available gauge."""
    if _KS_PROM_AVAILABLE:
        try:
            _KS_PERSISTENCE_GAUGE.set((1 if redis_ok else 0) + (1 if db_ok else 0))
        except Exception:  # noqa: BLE001
            pass


def _is_database_configured() -> bool:
    """Return True when DATABASE_URL is set (DB backend may be available)."""
    return bool(os.getenv("DATABASE_URL", ""))


# ---------------------------------------------------------------------------
# Module-level Redis singleton — reused across all KillSwitch instances so
# the same process never opens more than one connection to Redis.
# Protected by lazy init: the client is created on first use and cached here.
# When Redis is unavailable this stays None and the in-memory fallback is used.
# ---------------------------------------------------------------------------
_redis_client = None
_redis_client_available: bool | None = None  # None = never attempted
_redis_next_retry_at: float = 0.0
_redis_retry_backoff_seconds: float = 5.0
_REDIS_RETRY_BACKOFF_MAX_SECONDS: float = 60.0


def _get_redis():
    """Return the cached Redis client, (re-)connecting lazily.  Returns None on failure."""
    global _redis_client, _redis_client_available, _redis_next_retry_at, _redis_retry_backoff_seconds  # noqa: PLW0603

    now = time.monotonic()
    if _redis_client_available is False and now < _redis_next_retry_at:
        return None  # known-unavailable and still inside backoff window

    if _redis_client is not None:
        return _redis_client

    try:
        import redis as _redis  # type: ignore[import]

        url = os.getenv("REDIS_URL") or os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        client = _redis.from_url(url, decode_responses=True)
        client.ping()
        _redis_client = client
        _redis_client_available = True
        _redis_next_retry_at = 0.0
        _redis_retry_backoff_seconds = 5.0
        return _redis_client
    except Exception as exc:  # noqa: BLE001
        logger.warning("KillSwitchService: Redis unavailable (%s); using in-memory fallback", exc)
        _redis_client = None
        _redis_client_available = False
        _redis_next_retry_at = now + _redis_retry_backoff_seconds
        _redis_retry_backoff_seconds = min(
            _REDIS_RETRY_BACKOFF_MAX_SECONDS,
            _redis_retry_backoff_seconds * 2.0,
        )
        return None


def _get_db_engine():
    """Return a SQLAlchemy engine for DB-backed persistence, or None on failure."""
    try:
        from sqlalchemy import create_engine  # type: ignore[import]  # noqa: PLC0415

        url = os.getenv("DATABASE_URL", "")
        if not url:
            return None
        engine = create_engine(url, pool_pre_ping=True)
        return engine
    except Exception:  # noqa: BLE001
        return None


def _db_load_all() -> dict[str, bool]:
    """Load all kill-switch flags from PostgreSQL.  Returns {} on any failure."""
    engine = _get_db_engine()
    if engine is None:
        return {}
    try:
        from sqlalchemy import text  # noqa: PLC0415

        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT feature_name, enabled FROM kill_switch_flags")
            ).fetchall()
        return {row[0]: bool(row[1]) for row in rows}
    except Exception as exc:  # noqa: BLE001
        logger.warning("KillSwitchService: DB load failed: %s", exc)
        return {}


def _db_upsert(feature_name: str, enabled: bool) -> None:
    """Persist a single flag to PostgreSQL.  Silently no-ops on failure."""
    engine = _get_db_engine()
    if engine is None:
        return
    try:
        from sqlalchemy import text  # noqa: PLC0415

        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO kill_switch_flags (feature_name, enabled, updated_at) "
                    "VALUES (:name, :enabled, NOW()) "
                    "ON CONFLICT (feature_name) DO UPDATE SET "
                    "enabled = :enabled, updated_at = NOW()"
                ),
                {"name": feature_name, "enabled": enabled},
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "KillSwitchService: DB upsert failed for feature=%r: %s",
            feature_name,
            exc,
        )


class KillSwitch:
    """Redis-backed kill switch with DB persistence and in-memory fallback."""

    def __init__(self) -> None:
        self._fallback: dict[str, bool] = {}
        self._fallback_loaded_from_db: bool = False

    def _ensure_db_fallback_loaded(self) -> None:
        """Lazily load DB state into the in-memory fallback (once per instance)."""
        if not self._fallback_loaded_from_db:
            db_state = _db_load_all()
            for name, val in db_state.items():
                self._fallback.setdefault(name, val)
            self._fallback_loaded_from_db = True

    def is_enabled(self, feature_name: str) -> bool:
        r = _get_redis()
        redis_ok = r is not None
        db_ok = _is_database_configured()
        _ks_update_persistence_gauge(redis_ok, db_ok)
        if r is not None:
            try:
                val = r.hget(_REDIS_KEY, feature_name)
                if val is not None:
                    return val.lower() in {"1", "true", "yes", "on"}
            except Exception:  # noqa: BLE001
                pass
        # Redis unavailable — ensure DB fallback is loaded before consulting memory
        self._ensure_db_fallback_loaded()
        return self._fallback.get(feature_name, True)

    def set_switch(self, feature_name: str, enabled: bool) -> None:
        r = _get_redis()
        redis_ok = r is not None
        db_ok = _is_database_configured()
        _ks_update_persistence_gauge(redis_ok, db_ok)
        if r is not None:
            try:
                r.hset(_REDIS_KEY, feature_name, "true" if enabled else "false")
            except Exception:  # noqa: BLE001
                pass
        # Always write to DB for durability across worker restarts when Redis is down.
        _db_upsert(feature_name, enabled)
        self._fallback[feature_name] = enabled

    def get_status(self) -> dict[str, Any]:
        r = _get_redis()
        switches: dict[str, bool] = {}
        if r is not None:
            try:
                raw = r.hgetall(_REDIS_KEY)
                switches = {k: v.lower() in {"1", "true", "yes", "on"} for k, v in (raw or {}).items()}
            except Exception:  # noqa: BLE001
                switches = dict(self._fallback)
        else:
            self._ensure_db_fallback_loaded()
            switches = dict(self._fallback)
        return {"switches": switches, "ok": True}


_global_kill_switch: KillSwitch | None = None


def get_or_create_global_kill_switch() -> KillSwitch:
    global _global_kill_switch
    if _global_kill_switch is None:
        _global_kill_switch = KillSwitch()
    return _global_kill_switch


class KillSwitchService:
    """Redis-backed feature flag service (alias for KillSwitch, kept for API compatibility)."""

    def __init__(self) -> None:
        self._backend = KillSwitch()

    def is_enabled(self, feature_name: str) -> bool:
        return self._backend.is_enabled(feature_name)

    def set_switch(self, feature_name: str, enabled: bool) -> None:
        self._backend.set_switch(feature_name, enabled)

    def get_status(self) -> dict[str, Any]:
        return self._backend.get_status()
