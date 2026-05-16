"""
Seedance 2.0 provider configuration.

ALL Seedance / Kie AI settings live exclusively in backend environment variables.
NEVER expose these values to Next.js (.env.local) or Vite (.env) frontends.

Required env vars:
    SEEDANCE_API_KEY        — your kie.ai API key
    SEEDANCE_API_BASE_URL   — default: https://api.kie.ai
    SEEDANCE_MODEL          — default: bytedance/seedance-2-fast
    SEEDANCE_TIMEOUT        — default: 900
    SEEDANCE_PROVIDER       — label only, default: kie
    MAX_CONCURRENT_RENDER   — must stay 1 for sequential safety
    RENDER_MODE             — must be "sequential"
"""
from __future__ import annotations

import os


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise EnvironmentError(
            f"Missing required backend env var: {name}. "
            "Set it in backend/.env — do NOT add to Next.js .env.local or Vite .env."
        )
    return value


def _get(name: str, default: str) -> str:
    return os.environ.get(name, default).strip() or default


class SeedanceConfig:
    """Reads Seedance 2.0 runtime config from backend environment only."""

    @property
    def api_key(self) -> str:
        return _require("SEEDANCE_API_KEY")

    @property
    def api_base_url(self) -> str:
        return _get("SEEDANCE_API_BASE_URL", "https://api.kie.ai")

    @property
    def model(self) -> str:
        return _get("SEEDANCE_MODEL", "bytedance/seedance-2-fast")

    @property
    def timeout_seconds(self) -> int:
        return int(_get("SEEDANCE_TIMEOUT", "900"))

    @property
    def provider_label(self) -> str:
        return _get("SEEDANCE_PROVIDER", "kie")

    @property
    def max_concurrent_render(self) -> int:
        raw = _get("MAX_CONCURRENT_RENDER", "1")
        value = int(raw)
        if value != 1:
            raise EnvironmentError(
                f"MAX_CONCURRENT_RENDER must be 1 (sequential safety). Got: {value}"
            )
        return value

    @property
    def render_mode(self) -> str:
        mode = _get("RENDER_MODE", "sequential")
        if mode != "sequential":
            raise EnvironmentError(
                f"RENDER_MODE must be 'sequential'. Got: {mode}"
            )
        return mode

    def is_configured(self) -> bool:
        """Returns True if SEEDANCE_API_KEY is present in environment."""
        return bool(os.environ.get("SEEDANCE_API_KEY", "").strip())


# Module-level singleton — import this everywhere
seedance_config = SeedanceConfig()
