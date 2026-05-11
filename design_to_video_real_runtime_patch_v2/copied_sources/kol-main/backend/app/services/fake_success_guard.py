from __future__ import annotations

import os
from typing import Any

# All recognised fake-success markers checked by default.
_DEFAULT_MARKERS: tuple[str, ...] = (
    "example.invalid",
    "mock-output",
    "MOCK_SUCCEEDED",
    "drama-tts-stub",
    "'mock': True",
    '"mock": True',
    '"mock":true',
    "ark-stub",
)


class FakeSuccessError(RuntimeError):
    pass


def _hardlock_enabled() -> bool:
    return os.getenv("CI_HARDLOCK_FAKE_SUCCESS", "false").strip().lower() in {"1", "true", "yes", "on"}


def _is_production_or_staging() -> bool:
    """Return True for production *and* staging so stub URLs are caught in both environments."""
    return os.getenv("APP_ENV", "").strip().lower() in {"prod", "production", "staging"}


def assert_no_fake_success_payload(
    payload: dict[str, Any] | None,
    *,
    context: str = "",
    skip_markers: frozenset[str] | None = None,
) -> None:
    """Assert that *payload* does not contain any fake-success marker.

    Parameters
    ----------
    payload:
        The response dict to inspect.  No-ops when ``None`` or empty.
    context:
        Human-readable label included in :class:`FakeSuccessError` messages
        to help ops identify which code path produced the fake payload.
    skip_markers:
        Optional set of marker strings to exclude from the check for this
        specific call site.  Every entry must be a known marker from
        :data:`_DEFAULT_MARKERS`; unknown values raise :class:`ValueError`
        immediately so typos are caught at test/startup time rather than
        silently allowing fake payloads through.

        Use sparingly — only when legitimate business data is confirmed to
        contain a marker string and a false positive has been diagnosed.
        Example::

            assert_no_fake_success_payload(
                result,
                context="thumbnail_url_check",
                skip_markers=frozenset({"example.invalid"}),
            )

    Raises
    ------
    ValueError
        If *skip_markers* contains a string that is not in ``_DEFAULT_MARKERS``.
    FakeSuccessError
        If the payload contains a fake-success marker in a production or
        hardlock-enabled environment.
    """
    if not payload:
        return

    if skip_markers:
        unknown = skip_markers - set(_DEFAULT_MARKERS)
        if unknown:
            raise ValueError(
                f"assert_no_fake_success_payload: unknown skip_markers {unknown!r}. "
                f"Valid markers are: {_DEFAULT_MARKERS}"
            )

    active_markers = (
        tuple(m for m in _DEFAULT_MARKERS if m not in skip_markers)
        if skip_markers
        else _DEFAULT_MARKERS
    )

    serialized = str(payload)
    has_fake = any(marker in serialized for marker in active_markers)
    if has_fake and (_hardlock_enabled() or _is_production_or_staging()):
        raise FakeSuccessError(f"Fake success payload blocked in {context or 'unknown context'}")
