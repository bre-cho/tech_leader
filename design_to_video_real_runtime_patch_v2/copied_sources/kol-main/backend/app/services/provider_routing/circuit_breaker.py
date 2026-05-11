"""Redis-backed circuit breaker for video provider failover protection.

State machine per provider:

  CLOSED    → Normal operation.  Failures are counted in Redis.
              Trips to OPEN after *failure_threshold* consecutive failures.

  OPEN      → All requests are blocked.  After *recovery_timeout_seconds*
              elapses the breaker auto-transitions to HALF_OPEN on the next
              :meth:`~ProviderCircuitBreaker.is_open` call.

  HALF_OPEN → One probe request is allowed through.
              :meth:`~ProviderCircuitBreaker.record_success` → CLOSED.
              :meth:`~ProviderCircuitBreaker.record_failure`  → re-trips to OPEN.

Degraded mode
-------------
When Redis is unreachable (``_redis_unavailable=True``) all operations are
no-ops and :meth:`~ProviderCircuitBreaker.is_open` always returns ``False``.
This ensures a Redis outage never blocks provider traffic.

Process-local cache
-------------------
:func:`get_breaker` caches one :class:`ProviderCircuitBreaker` instance per
provider per process.  Instances are evicted via :func:`invalidate_breaker_cache`.
"""
from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass

import logging as _logging

_logger = _logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level flag: set to True when any ProviderCircuitBreaker falls back to
# in-process state because Redis is unavailable.  Exposed as a Prometheus
# metric so ops can alert on cross-process protection loss.
# ---------------------------------------------------------------------------
redis_unavailable_active: bool = False

KNOWN_PROVIDERS: tuple[str, ...] = ("veo", "runway", "kling", "seedance", "seedance2")


def _cb_count_open(provider: str) -> None:
    _logger.info("METRIC circuit_breaker_open_total provider=%s", provider)


def _cb_count_half_open(provider: str) -> None:
    _logger.info("METRIC circuit_breaker_half_open_total provider=%s", provider)


def _cb_set_redis_unavailable(active: bool) -> None:
    global redis_unavailable_active
    redis_unavailable_active = bool(active)

# ---------------------------------------------------------------------------
# State constants
# ---------------------------------------------------------------------------

_STATE_CLOSED = "CLOSED"
_STATE_OPEN = "OPEN"
_STATE_HALF_OPEN = "HALF_OPEN"

_KEY_PREFIX = "circuit"


# ---------------------------------------------------------------------------
# Public exceptions
# ---------------------------------------------------------------------------


class CircuitOpenError(RuntimeError):
    """Raised by :meth:`ProviderCircuitBreaker.assert_closed` when OPEN.

    Attributes
    ----------
    provider:
        Normalised provider key (e.g. ``"veo"``).
    retry_after:
        Approximate seconds remaining until the circuit auto-transitions to
        HALF_OPEN.  May be 0.0 when the timeout has already elapsed.
    """

    def __init__(self, provider: str, retry_after: float) -> None:
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker OPEN for provider={provider!r}; "
            f"retry after {retry_after:.1f}s"
        )


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------


@dataclass
class CircuitBreakerConfig:
    """Tunable parameters for a :class:`ProviderCircuitBreaker`.

    Parameters
    ----------
    failure_threshold:
        Number of consecutive failures that trip the circuit to OPEN.
    recovery_timeout_seconds:
        Seconds the circuit stays OPEN before auto-transitioning to HALF_OPEN.
    """

    failure_threshold: int = 3
    recovery_timeout_seconds: int = 60


# ---------------------------------------------------------------------------
# Core breaker
# ---------------------------------------------------------------------------


class ProviderCircuitBreaker:
    """Redis-backed circuit breaker for a single video provider.

    When Redis is available the circuit state is stored in Redis so all worker
    processes share a single source of truth.

    When Redis is unavailable (``_redis_unavailable=True``) an in-process
    fallback state machine takes over.  The fallback provides basic protection
    for the current worker process: it trips to OPEN after *failure_threshold*
    consecutive in-process failures and auto-recovers to HALF_OPEN after
    *recovery_timeout_seconds*.  Failures in other worker processes are not
    visible to the fallback — this is an acceptable trade-off that ensures a
    Redis outage never removes *all* circuit protection.

    Parameters
    ----------
    provider:
        Provider name (normalised to lowercase).
    config:
        Tunable parameters.  Defaults to :class:`CircuitBreakerConfig` with
        values from ``PROVIDER_CIRCUIT_BREAKER_FAILURE_THRESHOLD`` and
        ``PROVIDER_CIRCUIT_BREAKER_COOLDOWN_SECONDS`` env vars when ``None``.
    redis_url:
        Redis connection string.  Falls back to the ``REDIS_URL`` env var and
        then ``redis://localhost:6379/0``.
    """

    def __init__(
        self,
        provider: str,
        *,
        config: CircuitBreakerConfig | None = None,
        redis_url: str | None = None,
    ) -> None:
        self._provider = str(provider or "unknown").strip().lower()
        if config is None:
            config = CircuitBreakerConfig(
                failure_threshold=_env_int("PROVIDER_CIRCUIT_BREAKER_FAILURE_THRESHOLD", 3),
                recovery_timeout_seconds=_env_int("PROVIDER_CIRCUIT_BREAKER_COOLDOWN_SECONDS", 60),
            )
        self._config = config
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis = None  # lazy-connected
        self._redis_unavailable = False
        self._connect_lock = threading.Lock()

        # In-process fallback state — used only when Redis is unavailable.
        # Protected by _local_lock so concurrent threads don't race on the counters.
        self._local_lock = threading.Lock()
        self._local_failures: int = 0
        self._local_state: str = _STATE_CLOSED
        self._local_tripped_at: float | None = None

    # ------------------------------------------------------------------
    # Redis key helpers
    # ------------------------------------------------------------------

    def _key(self, suffix: str) -> str:
        return f"{_KEY_PREFIX}:{self._provider}:{suffix}"

    # ------------------------------------------------------------------
    # Lazy Redis connectivity — degrades gracefully on error
    # ------------------------------------------------------------------

    def _get_redis(self):
        if self._redis_unavailable:
            return None
        if self._redis is not None:
            return self._redis
        with self._connect_lock:
            if self._redis is not None:
                return self._redis
            try:
                import redis as _redis_lib  # noqa: PLC0415

                client = _redis_lib.from_url(self._redis_url, decode_responses=True)
                client.ping()
                self._redis = client
                _cb_set_redis_unavailable(False)
            except Exception as _exc:  # noqa: BLE001
                self._redis_unavailable = True
                self._redis = None
                _cb_set_redis_unavailable(True)
                _logger.error(
                    "METRIC circuit_breaker_redis_unavailable=1 — ProviderCircuitBreaker "
                    "for provider=%r cannot connect to Redis (%s). "
                    "Falling back to in-process state: circuit state is NOT shared across "
                    "worker processes. Cross-process protection is degraded until Redis recovers.",
                    self._provider,
                    _exc,
                )
        return self._redis

    # ------------------------------------------------------------------
    # In-process fallback state machine
    # Used only when Redis is unavailable (_redis_unavailable=True).
    # Provides single-process circuit protection so a Redis outage does
    # not leave providers completely unguarded.
    # ------------------------------------------------------------------

    def _local_is_open(self) -> bool:
        """Return whether the in-process fallback state is OPEN."""
        with self._local_lock:
            if self._local_state == _STATE_OPEN:
                if self._local_tripped_at is not None:
                    elapsed = time.time() - self._local_tripped_at
                    if elapsed >= self._config.recovery_timeout_seconds:
                        # Auto-transition to HALF_OPEN
                        self._local_state = _STATE_HALF_OPEN
                        self._local_failures = 0
                        _cb_count_half_open(self._provider)
                        return False
                return True
            return False

    def _local_record_failure(self) -> None:
        """Increment the in-process failure counter and trip to OPEN if threshold reached.

        When Redis is unavailable the effective failure threshold is halved
        (``max(1, threshold // 2)``) so the local circuit trips faster and still
        protects the current worker process even though cross-process protection
        is degraded.  A warning is logged the first time the local circuit opens
        so operators are alerted immediately.

        Once the circuit is already OPEN the counter is not incremented further —
        additional failures carry no new information.  ``_local_failures`` is
        reset to 0 on the OPEN transition so the counter accurately reflects the
        number of failures that caused the current trip (not a cumulative total).
        """
        with self._local_lock:
            if self._local_state == _STATE_OPEN:
                # Already open — no further action until the circuit auto-recovers
                # to HALF_OPEN via _local_is_open() after the recovery timeout.
                return
            self._local_failures += 1
            effective_threshold = (
                max(1, self._config.failure_threshold // 2)
                if self._redis_unavailable
                else self._config.failure_threshold
            )
            if self._local_failures >= effective_threshold:
                self._local_state = _STATE_OPEN
                self._local_tripped_at = time.time()
                self._local_failures = 0  # reset so next trip starts from 0
                _cb_count_open(self._provider)
                _logger.warning(
                    "Circuit OPEN (local-only, Redis degraded) for provider=%r "
                    "after %d failure(s) (effective threshold=%d, configured=%d). "
                    "Cross-process protection is unavailable until Redis recovers.",
                    self._provider,
                    effective_threshold,
                    effective_threshold,
                    self._config.failure_threshold,
                )

    def _local_record_success(self) -> None:
        """Reset the in-process fallback state to CLOSED."""
        with self._local_lock:
            self._local_failures = 0
            self._local_state = _STATE_CLOSED
            self._local_tripped_at = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_open(self) -> bool:
        """Return ``True`` when the circuit is OPEN and requests should be blocked.

        Automatically transitions OPEN → HALF_OPEN when the recovery timeout
        has elapsed, returning ``False`` to allow one probe request.

        When Redis is unavailable the in-process fallback state machine is
        consulted instead so the circuit still provides protection.
        """
        r = self._get_redis()
        if r is None:
            return self._local_is_open()
        try:
            state = r.get(self._key("state"))
            if state == _STATE_OPEN:
                tripped_raw = r.get(self._key("tripped_at"))
                if tripped_raw is None:
                    return True
                elapsed = time.time() - float(tripped_raw)
                if elapsed >= self._config.recovery_timeout_seconds:
                    # Auto-transition to HALF_OPEN to allow one probe.
                    # Reset the failure counter so re-tripping only counts
                    # failures that occur *during* the half-open probe window,
                    # not failures accumulated before the circuit opened.
                    r.set(self._key("state"), _STATE_HALF_OPEN)
                    r.delete(self._key("failures"))
                    _cb_count_half_open(self._provider)
                    if self._try_acquire_half_open_probe(r):
                        return False
                    return True
                return True
            # HALF_OPEN: allow probe request through.
            # CLOSED (or absent): normal operation.
            return False
        except Exception:  # noqa: BLE001
            return False  # degrade gracefully

    def assert_closed(self) -> None:
        """Raise :class:`CircuitOpenError` if the circuit is OPEN.

        Callers that want to fail-fast before spending I/O budget on a provider
        call should invoke this before calling the provider adapter.

        Mirrors :meth:`is_open`: when the recovery timeout has elapsed the
        circuit is transitioned to HALF_OPEN and this method returns normally
        so the caller gets the same probe slot that :meth:`is_open` would grant.

        When Redis is unavailable the in-process fallback state machine is
        consulted, matching the behaviour of :meth:`is_open`.
        """
        r = self._get_redis()
        if r is None:
            # Use in-process fallback.
            with self._local_lock:
                if self._local_state != _STATE_OPEN:
                    return
                elapsed = time.time() - (self._local_tripped_at or 0)
                if elapsed >= self._config.recovery_timeout_seconds:
                    self._local_state = _STATE_HALF_OPEN
                    self._local_failures = 0
                    return
                retry_after = max(0.0, self._config.recovery_timeout_seconds - elapsed)
            raise CircuitOpenError(self._provider, retry_after)
        try:
            state = r.get(self._key("state"))
            if state != _STATE_OPEN:
                return
            tripped_raw = r.get(self._key("tripped_at"))
            elapsed = time.time() - float(tripped_raw or 0)
            if elapsed >= self._config.recovery_timeout_seconds:
                # Same OPEN→HALF_OPEN transition as is_open(): reset failure
                # counter so only probe-window failures count toward re-tripping.
                r.set(self._key("state"), _STATE_HALF_OPEN)
                r.delete(self._key("failures"))
                _cb_count_half_open(self._provider)
                return  # allow probe request through
            retry_after = max(0.0, self._config.recovery_timeout_seconds - elapsed)
            raise CircuitOpenError(self._provider, retry_after)
        except CircuitOpenError:
            raise
        except Exception:  # noqa: BLE001
            return  # degrade gracefully

    def record_failure(self) -> None:
        """Record a provider failure.

        Increments the Redis failure counter.  When the count reaches
        *failure_threshold* the circuit trips to OPEN.

        When Redis is unavailable the in-process fallback counter is incremented
        instead so the current worker process still tracks failure streaks.
        """
        r = self._get_redis()
        if r is None:
            self._local_record_failure()
            return
        try:
            count = r.incr(self._key("failures"))
            if count >= self._config.failure_threshold:
                r.set(self._key("state"), _STATE_OPEN)
                r.set(self._key("tripped_at"), str(time.time()))
                _cb_count_open(self._provider)
        except Exception:  # noqa: BLE001
            pass

    def record_success(self) -> None:
        """Record a provider success and reset the circuit to CLOSED.

        When Redis is unavailable the in-process fallback state is reset.
        """
        r = self._get_redis()
        if r is None:
            self._local_record_success()
            return
        try:
            self._reset(r)
        except Exception:  # noqa: BLE001
            pass

    def get_state(self) -> dict:
        """Return a snapshot of the current breaker state for observability.

        Always returns a dict with at least ``provider``, ``state``, and
        ``redis_available`` keys.  When Redis is unavailable the in-process
        fallback state is reported with ``redis_available=False``.
        """
        r = self._get_redis()
        if r is None:
            with self._local_lock:
                return {
                    "provider": self._provider,
                    "state": self._local_state,
                    "failures": self._local_failures,
                    "tripped_at": self._local_tripped_at,
                    "redis_available": False,
                }
        try:
            state = r.get(self._key("state")) or _STATE_CLOSED
            failures_raw = r.get(self._key("failures"))
            tripped_raw = r.get(self._key("tripped_at"))
            return {
                "provider": self._provider,
                "state": state,
                "failures": int(failures_raw) if failures_raw else 0,
                "tripped_at": float(tripped_raw) if tripped_raw else None,
                "redis_available": True,
            }
        except Exception:  # noqa: BLE001
            return {
                "provider": self._provider,
                "state": _STATE_CLOSED,
                "failures": 0,
                "tripped_at": None,
                "redis_available": False,
            }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _reset(self, r) -> None:
        r.delete(self._key("state"), self._key("failures"), self._key("tripped_at"))

    def _try_acquire_half_open_probe(self, redis_client) -> bool:
        """Try to claim the half-open probe slot.

        Returns True when this caller acquired the probe and may proceed with a
        trial request, or False when another worker already holds the probe.
        """
        try:
            token = str(time.time())
            key = self._key("half_open_probe")
            acquired = redis_client.set(
                key,
                token,
                nx=True,
                ex=max(1, int(self._config.recovery_timeout_seconds)),
            )
            return bool(acquired)
        except Exception:  # noqa: BLE001
            return True


# ---------------------------------------------------------------------------
# Process-local breaker cache
# ---------------------------------------------------------------------------

_BREAKERS: dict[str, ProviderCircuitBreaker] = {}
_BREAKERS_LOCK = threading.Lock()


def get_breaker(provider: str) -> ProviderCircuitBreaker:
    """Return (and cache) the :class:`ProviderCircuitBreaker` for *provider*.

    The cache uses the normalised (lowercase) provider key so ``get_breaker("VEO")``
    and ``get_breaker("veo")`` return the same instance.
    """
    key = str(provider or "unknown").strip().lower()
    with _BREAKERS_LOCK:
        breaker = _BREAKERS.get(key)
        if breaker is None:
            breaker = ProviderCircuitBreaker(key)
            _BREAKERS[key] = breaker
        return breaker


def invalidate_breaker_cache(provider: str | None = None) -> None:
    """Evict cached breaker instance(s) so they are re-created on next use.

    Parameters
    ----------
    provider:
        Specific provider to evict.  When ``None`` all cached instances are
        cleared (e.g. after a configuration change or in tests).
    """
    with _BREAKERS_LOCK:
        if provider is None:
            _BREAKERS.clear()
        else:
            _BREAKERS.pop(str(provider or "").strip().lower(), None)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default
