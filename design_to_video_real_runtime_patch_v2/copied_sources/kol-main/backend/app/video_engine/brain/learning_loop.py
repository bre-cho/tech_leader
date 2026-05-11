from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

_logger = logging.getLogger(__name__)

# Sentinel score returned when no real data is available.
_DEFAULT_SCORE = 0.5

# ---------------------------------------------------------------------------
# EWMA alpha configuration
# ---------------------------------------------------------------------------
# Override via env vars:
#   LEARNING_LOOP_ALPHA_LOW=0.1  — alpha used when samples < ALPHA_THRESHOLD
#   LEARNING_LOOP_ALPHA_HIGH=0.2 — alpha used when samples >= ALPHA_THRESHOLD
#   LEARNING_LOOP_ALPHA_THRESHOLD=20 — sample count boundary
# Defaults preserve the original hardcoded behaviour.

# ---------------------------------------------------------------------------
# _FileBackend max-samples cap (P10)
# ---------------------------------------------------------------------------
# Override via LEARNING_LOOP_FILE_MAX_KEYS to change the per-file cap on how
# many provider keys are retained.  When the cap is reached, the least-sampled
# entries are pruned so the file never grows without bound in long-running
# dev environments.
# Set to 0 to disable the cap entirely (unsafe for long-lived processes).
_FILE_BACKEND_MAX_KEYS_DEFAULT: int = 500

def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# NoOp backend activity flags — exposed as Prometheus metrics so ops can
# alert when learning signals are silently dropped.
# ---------------------------------------------------------------------------
# noop_backend_active     → set for ANY env that falls back to NoOp (dev/staging).
# staging_noop_backend_active → set ONLY in staging so ops can alert separately.
#   Alert rule: learning_loop_staging_noop_active == 1 for > 24h suggests
#   the staging deployment is misconfigured (missing DB session).
noop_backend_active: bool = False
staging_noop_backend_active: bool = False


class OutcomeValidationError(ValueError):
    """Raised when a learning-loop outcome payload is invalid."""


def _validate_outcome(outcome: Dict[str, Any]) -> None:
    provider = str(outcome.get("provider") or "").strip()
    if not provider:
        raise OutcomeValidationError("provider is required")

    quality = outcome.get("quality_score")
    if quality is not None and not (0.0 <= float(quality) <= 1.0):
        raise OutcomeValidationError("quality_score must be between 0 and 1")

    reference = outcome.get("reference_fidelity_score")
    if reference is not None and not (0.0 <= float(reference) <= 1.0):
        raise OutcomeValidationError("reference_fidelity_score must be between 0 and 1")

    latency = outcome.get("latency_ms")
    if latency is not None and float(latency) < 0.0:
        raise OutcomeValidationError("latency_ms must be >= 0")

    cost = outcome.get("cost_usd")
    if cost is not None and float(cost) < 0.0:
        raise OutcomeValidationError("cost_usd must be >= 0")


def _compute_score(outcome: Dict[str, Any]) -> float:
    """Compute a composite score from a provider outcome dict."""
    quality = float(outcome.get("quality_score") or 0.5)
    success = 1.0 if outcome.get("success") else 0.0
    ref = float(outcome.get("reference_fidelity_score") or quality)
    latency_ms = float(outcome.get("latency_ms") or 60000)
    cost = float(outcome.get("cost_usd") or 0.05)
    latency_score = max(0.0, min(1.0, 1.0 - latency_ms / 180000.0))
    cost_score = max(0.0, min(1.0, 1.0 - cost / 1.0))
    return quality * 0.40 + success * 0.25 + ref * 0.15 + latency_score * 0.10 + cost_score * 0.10


class _FileBackend:
    """JSON-file backend. Disabled in production/staging.

    Thread/process safety: uses a per-path :class:`threading.Lock` to
    serialise concurrent in-process ``put()`` calls, and an advisory
    ``<path>.lock`` file (via ``fcntl.flock``) to serialise cross-process
    writers on POSIX systems.  Both locks are held across the full
    load → modify → save cycle so no concurrent writer can see a stale read.

    On platforms where ``fcntl`` is unavailable (Windows) the cross-process
    lock is silently skipped — only the thread-level lock is active.
    """

    # Per-path thread locks shared across all _FileBackend instances in a process.
    _path_locks: dict[str, "threading.Lock"] = {}
    _path_locks_meta: "threading.Lock" = threading.Lock()
    # Hard cap on the number of distinct file paths tracked in _path_locks.
    # In long-running workers a continuously-changing LEARNING_LOOP_FILE_PATH
    # (e.g. date-stamped paths) would otherwise grow this dict without bound.
    # When the cap is reached the oldest entry is evicted FIFO; existing
    # _FileBackend instances retain their own strong reference via self._thread_lock
    # so eviction from the class dict never breaks an in-flight operation.
    _MAX_PATH_LOCKS: int = 1_000

    def __init__(self, path: str) -> None:
        import os as _os  # noqa: PLC0415

        from app.core.production_gate import is_production_env  # noqa: PLC0415

        app_env = _os.getenv("APP_ENV", "").strip().lower()
        # Block file backend in strict production envs and in any other env
        # that is_production_env() considers production-grade, except staging.
        # Staging is excluded so that LearningLoopStore can fall through to
        # _NoOpBackend there (with a warning) rather than crashing.
        is_file_blocked = app_env in {"production", "prod"} or (
            is_production_env() and app_env != "staging"
        )
        if is_file_blocked:
            raise RuntimeError(
                "LearningLoopStore file backend is disabled in production/staging. "
                "Set LEARNING_LOOP_BACKEND=db and ensure the video_provider_outcomes "
                "table exists (alembic upgrade head)."
            )
        self._path = Path(path)
        self._lock_path = Path(str(path) + ".lock")
        # Acquire or create the per-path thread lock.
        key = str(self._path.resolve())
        with _FileBackend._path_locks_meta:
            if key not in _FileBackend._path_locks:
                if len(_FileBackend._path_locks) >= _FileBackend._MAX_PATH_LOCKS:
                    # Evict the oldest entry (FIFO) to cap memory usage.
                    # Existing instances keep their own strong reference via
                    # self._thread_lock, so eviction never breaks live operations.
                    _FileBackend._path_locks.pop(next(iter(_FileBackend._path_locks)))
                _FileBackend._path_locks[key] = threading.Lock()
            # Read the lock reference while still holding _path_locks_meta so
            # a concurrent eviction of this key (theoretically impossible with
            # FIFO given it was just inserted at the tail, but guarded here for
            # correctness) cannot cause a KeyError between insertion and read.
            self._thread_lock: threading.Lock = _FileBackend._path_locks[key]

        # Warn when the file backend is used outside a test environment — it
        # relies on POSIX flock for cross-process safety, which only works when
        # all writers share the same filesystem mount.  Multiple Celery workers
        # on different hosts (e.g. Kubernetes pods) will each maintain an
        # independent copy of the JSON file and silently lose each other's
        # learning signals.  Pass db= to LearningLoopStore (or to
        # VideoBrainOrchestrator) to use the DB backend in all non-dev envs.
        if app_env not in {"test", "testing", ""}:
            _logger.warning(
                "LearningLoopStore._FileBackend: file-based backend is active in "
                "APP_ENV=%r.  This backend is safe for single-process development "
                "but NOT for multi-process/multi-host deployments (e.g. Celery "
                "workers on different pods).  Pass db= to LearningLoopStore to "
                "activate the DB backend and share learning signals across workers.",
                app_env,
            )

        # Warn on Windows where fcntl is unavailable and cross-process file
        # locking is silently skipped.  Concurrent writes from multiple processes
        # on the same machine can race and corrupt the JSON file.  Use the DB
        # backend (pass db= to LearningLoopStore) for any environment with more
        # than one writer process.
        try:
            import fcntl  # noqa: PLC0415, F401
        except ImportError:
            _logger.warning(
                "LearningLoopStore._FileBackend: fcntl is not available on this "
                "platform (Windows?).  Cross-process file locking is DISABLED — "
                "concurrent writes from multiple processes may corrupt %s.  "
                "Use the DB backend (pass db= to LearningLoopStore) to avoid this risk.",
                self._path,
            )

    @staticmethod
    def _flock_exclusive(fh) -> None:
        """Acquire an exclusive fcntl advisory lock on *fh*, silently skip on Windows."""
        try:
            import fcntl  # noqa: PLC0415
            fcntl.flock(fh, fcntl.LOCK_EX)
        except ImportError:
            pass

    @staticmethod
    def _funlock(fh) -> None:
        try:
            import fcntl  # noqa: PLC0415
            fcntl.flock(fh, fcntl.LOCK_UN)
        except ImportError:
            pass

    def _acquire_file_lock(self):
        """Open and exclusively lock the advisory lock file.

        Returns the open file handle that must be passed to ``_release_file_lock``.
        The lock file is separate from the data file so it survives atomic renames.
        """
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(self._lock_path, "a+", encoding="utf-8")  # noqa: WPS515
        try:
            self._flock_exclusive(fh)
        except Exception:  # noqa: BLE001
            # If locking fails, close the handle before re-raising so we don't leak it.
            try:
                fh.close()
            except Exception:  # noqa: BLE001
                pass
            raise
        return fh

    def _release_file_lock(self, fh) -> None:
        self._funlock(fh)
        try:
            fh.close()
        except Exception:  # noqa: BLE001
            pass

    def load(self) -> Dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                # Acquire a shared (read) advisory lock so we never read a
                # partially-written file while another process holds the
                # exclusive write lock inside put().  Silently skipped on
                # Windows where fcntl is unavailable.
                try:
                    import fcntl  # noqa: PLC0415
                    fcntl.flock(fh, fcntl.LOCK_SH)
                    try:
                        return json.loads(fh.read())
                    finally:
                        fcntl.flock(fh, fcntl.LOCK_UN)
                except ImportError:
                    return json.loads(fh.read())
        except Exception:
            return {}

    def save(self, data: Dict[str, Any]) -> None:
        # Write to a temp file then atomically rename to avoid partial writes.
        import tempfile  # noqa: PLC0415
        dir_ = str(self._path.parent)
        fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(data, indent=2, sort_keys=True))
            os.replace(tmp, self._path)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def get(self, key: str) -> Dict[str, Any] | None:
        return self.load().get(key)

    def list_all(self) -> Dict[str, Any]:
        """Return all stored provider records as a dict keyed by routing_profile_provider."""
        return self.load()

    def put(self, key: str, value: Dict[str, Any]) -> None:
        # Stamp each record with an ISO-8601 updated_at so the pruning strategy
        # can evict the *oldest* entries rather than the least-sampled ones.
        # Pruning by least-samples would evict new providers immediately when the
        # file is at capacity, preventing them from ever accumulating data.
        from datetime import datetime, timezone  # noqa: PLC0415

        value = dict(value)
        value.setdefault("updated_at", datetime.now(timezone.utc).isoformat())
        # Hold both the thread lock and the cross-process file lock for the
        # entire load → modify → save cycle to prevent lost-update races.
        with self._thread_lock:
            lock_fh = self._acquire_file_lock()
            try:
                data = self.load()
                data[key] = value
                # Prune oldest entries when the file grows beyond the configured cap
                # so the JSON file never bloats indefinitely in long-running dev
                # environments.  Oldest-first ensures recently-added providers
                # (potentially with low sample counts) are not evicted before they
                # have a chance to accumulate data.
                max_keys = _env_int("LEARNING_LOOP_FILE_MAX_KEYS", _FILE_BACKEND_MAX_KEYS_DEFAULT)
                if max_keys > 0 and len(data) > max_keys:
                    sorted_keys = sorted(
                        data,
                        key=lambda k: str((data[k] or {}).get("updated_at", "")),
                    )
                    excess = len(data) - max_keys
                    for pruned_key in sorted_keys[:excess]:
                        del data[pruned_key]
                self.save(data)
            finally:
                self._release_file_lock(lock_fh)


class _NoOpBackend:
    """No-op backend used when no DB session is available.

    Behaviour by environment
    ------------------------
    **production / prod** (``APP_ENV=production|prod``):
        Constructing ``_NoOpBackend`` is a hard ``RuntimeError`` — it means a
        caller created :class:`LearningLoopStore` without a DB session, which
        would silently drop every learning signal and degrade routing quality.
        The error surfaces at startup rather than at first use.

    **staging** (``APP_ENV=staging``):
        The backend is allowed but emits an ERROR log and sets the
        ``learning_loop_noop_active`` flag.  This lets staging environments
        run without a DB session while still surfacing the misconfiguration via
        Prometheus.  Pass ``db=`` to :class:`LearningLoopStore` (or to
        :class:`~app.video_engine.brain.orchestrator.VideoBrainOrchestrator`)
        to enable the DB backend and mirror production routing quality.

    **development / test** (all other envs):
        Silent no-op; ``get()`` returns ``None`` and ``put()`` is a no-op.
        Only expected in unit tests that run without a DB session.

    Operators should monitor the ``learning_loop_noop_active`` Prometheus gauge
    and alert when it is ``1``.
    """

    _warned: bool = False

    def __init__(self) -> None:
        import os as _os  # noqa: PLC0415

        from app.core.production_gate import is_production_env  # noqa: PLC0415

        app_env = _os.getenv("APP_ENV", "").strip().lower()
        # Strict production environments: hard fail to prevent silent signal loss.
        is_strict_production = app_env in {"production", "prod"}
        # Staging: permit NoOp but warn loudly so it shows up in Prometheus.
        is_staging = app_env == "staging"

        if is_strict_production:
            raise RuntimeError(
                "_NoOpBackend: no DB session provided in production. "
                "Pass db= to LearningLoopStore (or to ProviderDecisionEngine / "
                "VideoBrainOrchestrator) to use the DB backend and persist provider "
                "learning signals.  Running without db= in production silently drops "
                "every outcome signal and degrades routing quality over time."
            )

        # Non-strict but production-gated envs (staging) and dev/test all land here.
        global noop_backend_active, staging_noop_backend_active
        noop_backend_active = True
        if is_staging:
            staging_noop_backend_active = True
        if not _NoOpBackend._warned:
            if is_staging or is_production_env():
                _logger.error(
                    "METRIC learning_loop_noop_active=1 learning_loop_staging_noop_active=%d — "
                    "LearningLoopStore: no DB session provided in staging. Provider learning "
                    "bonuses will NOT be persisted and routing quality will NOT mirror production. "
                    "Pass db= to LearningLoopStore (or to ProviderDecisionEngine / "
                    "VideoBrainOrchestrator) to enable the DB backend and activate "
                    "production-quality routing. "
                    "Alert: set a Prometheus alert on learning_loop_staging_noop_active == 1 "
                    "for duration > 24h to catch misconfigured staging deployments.",
                    1 if is_staging else 0,
                )
            else:
                _logger.warning(
                    "LearningLoopStore: no DB session provided — using NoOp backend. "
                    "Learning signals will not be persisted (expected in unit tests)."
                )
            _NoOpBackend._warned = True

    def get(self, key: str) -> Dict[str, Any] | None:  # noqa: ARG002
        return None

    def put(self, key: str, value: Dict[str, Any]) -> None:  # noqa: ARG002
        pass

    def list_all(self) -> Dict[str, Any]:
        return {}


class _DbBackend:
    """DB-backed store using the ``video_provider_outcomes`` table.

    Parameters
    ----------
    db:
        Active SQLAlchemy session.
    auto_commit:
        When ``True`` (default) each ``put()`` call issues an immediate
        ``COMMIT`` so the write is durable before the method returns.
        Set to ``False`` when the caller manages its own transaction
        boundaries (e.g. a batch-update path that commits once after
        processing a whole batch of outcomes).  Callers that disable
        ``auto_commit`` are responsible for committing or rolling back the
        session themselves.
    """

    def __init__(self, db: "Session", *, auto_commit: bool = True) -> None:
        self._db = db
        self._auto_commit = auto_commit

    def get(self, key: str) -> Dict[str, Any] | None:
        from sqlalchemy import text  # noqa: PLC0415

        row = self._db.execute(
            text(
                "SELECT samples, score, fail_streak "
                "FROM video_provider_outcomes "
                "WHERE routing_profile_provider = :key "
                "LIMIT 1"
            ),
            {"key": key},
        ).fetchone()
        if row is None:
            return None
        return {
            "samples": int(row.samples),
            "score": float(row.score),
            "fail_streak": int(row.fail_streak),
        }

    def list_all(self) -> Dict[str, Any]:
        """Return all rows from ``video_provider_outcomes`` as a dict keyed by routing_profile_provider."""
        from sqlalchemy import text  # noqa: PLC0415

        rows = self._db.execute(
            text(
                "SELECT routing_profile_provider, samples, score, fail_streak "
                "FROM video_provider_outcomes"
            )
        ).fetchall()
        return {
            row.routing_profile_provider: {
                "samples": int(row.samples),
                "score": float(row.score),
                "fail_streak": int(row.fail_streak),
            }
            for row in rows
        }

    def put(self, key: str, value: Dict[str, Any]) -> None:
        from sqlalchemy import text  # noqa: PLC0415

        self._db.execute(
            text(
                "INSERT INTO video_provider_outcomes "
                "(routing_profile_provider, samples, score, fail_streak, updated_at) "
                "VALUES (:key, :samples, :score, :fail_streak, :updated_at) "
                "ON CONFLICT (routing_profile_provider) DO UPDATE SET "
                "samples = :samples, score = :score, fail_streak = :fail_streak, "
                "updated_at = :updated_at"
            ),
            {
                "key": key,
                "samples": int(value["samples"]),
                "score": float(value["score"]),
                "fail_streak": int(value["fail_streak"]),
                "updated_at": _utcnow(),
            },
        )
        if self._auto_commit:
            try:
                self._db.commit()
            except Exception as exc:  # noqa: BLE001
                _logger.warning("LearningLoopStore DB commit failed: %s", exc)
                self._db.rollback()


def _utcnow():
    from datetime import datetime, timezone  # noqa: PLC0415

    return datetime.now(timezone.utc).replace(tzinfo=None)


class LearningLoopStore:
    """Provider outcome learning store.

    In development the store is backed by a JSON file (``path`` argument).
    In production **a SQLAlchemy ``db`` session must be supplied**; omitting it
    raises :class:`RuntimeError` (via :class:`_NoOpBackend`) so misconfigured
    callers fail fast rather than silently dropping all learning signals.

    In staging (``APP_ENV=staging``) the store accepts ``db=None`` and uses a
    :class:`_NoOpBackend` that logs errors and flips the
    ``learning_loop_noop_active`` Prometheus gauge to ``1``.  This allows
    staging environments to run without a DB session while the misconfiguration
    is surfaced through monitoring.  Passing ``db=`` in staging activates the
    full :class:`_DbBackend` path, which mirrors production routing quality.

    Passing a ``db`` session always takes precedence over the file backend
    regardless of environment.

    Production path: DB table ``video_provider_outcomes``
    (see alembic migration 20260502_0043).

    Parameters
    ----------
    path:
        Path to the JSON file used by the development :class:`_FileBackend`.
        Ignored when ``db`` is provided or when running in production/staging.
    db:
        SQLAlchemy session for the production :class:`_DbBackend`.
    db_auto_commit:
        Forwarded to :class:`_DbBackend` as ``auto_commit``.  Default ``True``
        preserves backward-compatible behaviour (commit after every
        ``record_outcome``).  Set to ``False`` when the caller manages its own
        transaction boundaries to enable batch-commit patterns.
    """

    def __init__(
        self,
        path: str = "/tmp/video_provider_learning.json",
        db: "Session | None" = None,
        *,
        db_auto_commit: bool = True,
    ) -> None:
        if db is not None:
            self._backend: _FileBackend | _DbBackend | _NoOpBackend = _DbBackend(db, auto_commit=db_auto_commit)
        else:
            import os as _os  # noqa: PLC0415

            from app.core.production_gate import is_production_env  # noqa: PLC0415

            app_env = _os.getenv("APP_ENV", "").strip().lower()
            if is_production_env() or app_env in {"production", "prod", "staging"}:
                # In production: _NoOpBackend.__init__ raises RuntimeError.
                # In staging:    _NoOpBackend.__init__ logs an error and sets the
                #                Prometheus flag but does NOT raise, allowing the
                #                process to continue with degraded (no-op) routing.
                self._backend = _NoOpBackend()
            else:
                self._backend = _FileBackend(path)

    def record_outcome(self, outcome: Dict[str, Any]) -> Dict[str, Any]:
        _validate_outcome(outcome)
        provider = outcome["provider"]
        profile = outcome.get("routing_profile", "default")
        key = f"{profile}:{provider}"
        current = self._backend.get(key) or {"samples": 0, "score": _DEFAULT_SCORE, "fail_streak": 0}
        raw = _compute_score(outcome)
        samples = int(current["samples"]) + 1
        alpha_threshold = _env_int("LEARNING_LOOP_ALPHA_THRESHOLD", 20)
        alpha_high = _env_float("LEARNING_LOOP_ALPHA_HIGH", 0.2)
        alpha_low = _env_float("LEARNING_LOOP_ALPHA_LOW", 0.1)
        alpha = alpha_high if samples >= alpha_threshold else alpha_low
        current["score"] = round((1 - alpha) * float(current["score"]) + alpha * raw, 4)
        current["samples"] = samples
        success = bool(outcome.get("success"))
        current["fail_streak"] = 0 if success else int(current.get("fail_streak", 0)) + 1
        self._backend.put(key, current)
        return current

    def provider_bonus(self, routing_profile: str, provider: str) -> float:
        item = self._backend.get(f"{routing_profile}:{provider}")
        if not item:
            return 0.0
        if item.get("samples", 0) < 20:
            return 0.0
        if item.get("fail_streak", 0) >= 3:
            return -0.30
        return (float(item.get("score", _DEFAULT_SCORE)) - _DEFAULT_SCORE) * 0.25

    def snapshot_all(self) -> Dict[str, Any]:
        """Return all stored EWMA records as a dict keyed by ``profile:provider``.

        Useful for exposing per-provider Prometheus metrics without coupling
        the collector to the backend implementation.  Returns an empty dict
        when the backend has no data (NoOp backend or empty file/DB).
        """
        return self._backend.list_all()
