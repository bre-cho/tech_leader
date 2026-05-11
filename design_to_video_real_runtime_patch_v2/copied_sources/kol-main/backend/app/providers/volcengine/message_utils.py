from typing import Any


def build_multimodal_user_message(*, prompt: str, image_url: str) -> dict[str, Any]:
    if not prompt or not prompt.strip():
        raise ValueError("prompt must not be empty")
    if not image_url or not image_url.strip():
        raise ValueError("image_url must not be empty")

    return {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_url}},
            {"type": "text", "text": prompt},
        ],
    }
