from __future__ import annotations

import os
from typing import Any

from app.core.production_gate import ensure_stub_allowed


def build_multimodal_user_message(*, text: str, image_url: str) -> dict[str, Any]:
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": image_url}},
        ],
    }


def ark_chat_completion(*, model: str, messages: list[dict[str, Any]], max_tokens: int | None = None) -> dict[str, Any]:
    """Call the Ark multimodal completion API (ByteDance/Volcano Ark).

    Real API call: set ``ARK_API_KEY`` and ``ARK_BASE_URL`` (default:
    ``https://ark.cn-beijing.volces.com/api/v3``).

    When ``ARK_API_KEY`` is absent the function falls back to a clearly-labelled
    stub that is blocked in production by ``ensure_stub_allowed()``.  Set
    ``ALLOW_ARK_STUB=true`` only in non-production environments.
    """
    api_key = os.getenv("ARK_API_KEY", "").strip()
    base_url = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").strip()

    if api_key:
        import urllib.request  # noqa: PLC0415
        import json as _json  # noqa: PLC0415

        body = _json.dumps(
            {
                "model": model,
                "messages": messages,
                **({"max_tokens": max_tokens} if max_tokens is not None else {}),
            },
            ensure_ascii=False,
        ).encode()
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        timeout = int(os.getenv("ARK_TIMEOUT_SECONDS", "60"))
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            result: dict[str, Any] = _json.loads(resp.read())
        # Extract first choice content for convenience
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            content = None
        return {
            "provider": "ark",
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "stub": False,
            "content": content,
            "raw": result,
        }

    # No API key configured — stub fallback.
    # In production/staging: always raise regardless of ALLOW_ARK_STUB so that
    # a missing ARK_API_KEY is never silently papered over with a stub response
    # that carries the [ark-stub] fake-success marker.
    from app.core.production_gate import is_production_or_staging  # noqa: PLC0415

    if is_production_or_staging():
        raise RuntimeError(
            "ARK_API_KEY is required in production/staging but is not set. "
            "Configure ARK_API_KEY to enable the Ark multimodal client. "
            "Stub responses are never permitted in production or staging environments."
        )
    ensure_stub_allowed("Ark multimodal client", allow_env="ALLOW_ARK_STUB")
    return {
        "provider": "ark",
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "stub": True,
        "content": "Ark multimodal client stub response. [ark-stub]",
    }
