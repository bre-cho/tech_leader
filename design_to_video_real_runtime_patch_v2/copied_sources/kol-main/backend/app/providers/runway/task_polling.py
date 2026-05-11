from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

from app.core.config import settings
from app.schemas.provider_common import NormalizedStatusResult


async def poll_runway_task(
    query_fn: Callable[[], Awaitable[NormalizedStatusResult]],
    *,
    timeout_seconds: int | None = None,
    interval_seconds: float | None = None,
) -> NormalizedStatusResult:
    """
    Generic async polling helper for Runway tasks.

    Runway's SDKs provide built-in task polling. This helper mirrors that behavior
    for REST-based integrations inside Visual Engine V4.
    """
    timeout = timeout_seconds or getattr(settings, "runway_poll_timeout_seconds", 600)
    interval = interval_seconds or getattr(settings, "runway_poll_interval_seconds", 5.0)

    elapsed = 0.0
    last: NormalizedStatusResult | None = None

    while elapsed <= timeout:
        last = await query_fn()
        if last.state in {"succeeded", "failed", "canceled"}:
            return last

        await asyncio.sleep(interval)
        elapsed += interval

    if last is not None:
        last.state = "failed"
        last.error_message = f"Runway task polling timed out after {timeout} seconds"
        return last

    raise TimeoutError(f"Runway task polling timed out after {timeout} seconds")
