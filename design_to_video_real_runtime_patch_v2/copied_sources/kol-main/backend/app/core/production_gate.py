from __future__ import annotations

import os


class ProductionGateError(RuntimeError):
    pass


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def is_production_env() -> bool:
    """Return True only when APP_ENV is explicitly set to 'production' or 'prod'."""
    app_env = os.getenv("APP_ENV", "").strip().lower()
    return app_env in {"prod", "production"}


def is_production_or_staging() -> bool:
    """Return True when APP_ENV is production *or* staging.

    Use this guard wherever mock/simulated components must be blocked not only
    in production but also in staging environments (i.e. any environment that
    receives real traffic or is considered production-like).
    """
    app_env = os.getenv("APP_ENV", "").strip().lower()
    return app_env in {"prod", "production", "staging"}


def ensure_stub_allowed(reason: str, *, allow_env: str = "ALLOW_STUBS") -> None:
    if is_production_or_staging() and not env_bool(allow_env, False):
        raise ProductionGateError(f"Stub not allowed in production/staging: {reason}")
