from __future__ import annotations

import os


def cli_synthetic_fallback_enabled(*, no_synthetic_fallback: bool) -> bool:
    """Return CLI synthetic-fallback mode with production-like hard disable."""
    if os.getenv("APP_ENV", "").strip().lower() in {"prod", "production", "staging"}:
        return False
    return not no_synthetic_fallback
