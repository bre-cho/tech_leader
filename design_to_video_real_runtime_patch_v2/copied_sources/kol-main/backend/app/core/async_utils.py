from __future__ import annotations

import asyncio
from typing import Awaitable, TypeVar

T = TypeVar("T")


def run_async(awaitable: Awaitable[T]) -> T:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(awaitable)

    new_loop = asyncio.new_event_loop()
    try:
        return new_loop.run_until_complete(awaitable)
    finally:
        new_loop.close()
