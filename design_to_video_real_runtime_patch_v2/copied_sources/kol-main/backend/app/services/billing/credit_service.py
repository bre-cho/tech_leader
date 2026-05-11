from __future__ import annotations

from typing import Any


def require_credits(
    _db: Any,
    _team_id: str,
    *,
    source: str,
    subject_type: str,
    subject_id: str,
    user_id: str | None = None,
) -> None:
    """Compatibility no-op credit guard."""
    return None
