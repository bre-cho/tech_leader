from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from app.providers.volcengine.client import VolcengineArkClient
from app.providers.volcengine.config import settings
from app.providers.volcengine.message_utils import build_multimodal_user_message
from app.providers.volcengine.router import VolcengineCapabilityRouter


class VolcengineChatRequest(BaseModel):
    messages: list[dict[str, object]]
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 1024


class VolcengineVisionChatRequest(BaseModel):
    image_url: HttpUrl
    prompt: str = Field(min_length=1)
    model: str | None = None
    max_tokens: int = 1024


router = APIRouter(prefix="/api/v1/providers/volcengine", tags=["providers-volcengine"])


@router.get("/capabilities")
async def volcengine_capabilities():
    return VolcengineCapabilityRouter().capabilities()


@router.post("/chat")
async def volcengine_chat(payload: VolcengineChatRequest):
    client = VolcengineArkClient()
    try:
        return await client.chat_completion(
            messages=payload.messages,
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Volcengine chat failed: {exc}") from exc


@router.post("/vision/chat")
async def volcengine_vision_chat(payload: VolcengineVisionChatRequest):
    client = VolcengineArkClient()
    message = build_multimodal_user_message(
        prompt=payload.prompt,
        image_url=str(payload.image_url),
    )
    try:
        return await client.chat_completion(
            messages=[message],
            model=payload.model,
            max_tokens=payload.max_tokens,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Volcengine vision chat failed: {exc}") from exc


@router.get("/health")
async def volcengine_health():
    if not settings.VOLCENGINE_ENABLED:
        return {"ok": False, "provider": "volcengine", "reason": "VOLCENGINE_ENABLED=false"}
    if not settings.VOLCENGINE_ARK_API_KEY:
        return {"ok": False, "provider": "volcengine", "reason": "VOLCENGINE_ARK_API_KEY missing"}

    client = VolcengineArkClient()
    try:
        return await client.healthcheck()
    except Exception as primary_error:  # noqa: BLE001
        if settings.VOLCENGINE_ARK_FALLBACK_BASE_URL:
            try:
                fallback = VolcengineArkClient(base_url=settings.VOLCENGINE_ARK_FALLBACK_BASE_URL)
                data = await fallback.healthcheck()
                data["fallback_used"] = True
                return data
            except Exception as fallback_error:  # noqa: BLE001
                return {
                    "ok": False,
                    "provider": "volcengine",
                    "primary_error": str(primary_error),
                    "fallback_error": str(fallback_error),
                }
        return {"ok": False, "provider": "volcengine", "error": str(primary_error)}
