from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from app.providers.seedance import SeedanceClient, SeedanceCreateRequest, SeedanceTask
from app.services.llm.ark_multimodal_client import ark_chat_completion, build_multimodal_user_message


router = APIRouter(prefix="/api/v1/providers/seedance", tags=["providers-seedance"])


class ArkVisionChatRequest(BaseModel):
    image_url: HttpUrl
    prompt: str = Field(default="What is the person doing in this picture?", min_length=1)
    model: str = "seed-1-8-251228"
    max_tokens: int | None = None


class SeedanceProbeRequest(BaseModel):
    stop_on_first_usable: bool = False


@router.post("/tasks", response_model=SeedanceTask)
async def create_seedance_task(payload: SeedanceCreateRequest):
    try:
        return await SeedanceClient().create_task(payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Seedance create task failed: {exc}") from exc


@router.get("/tasks/{task_id}", response_model=SeedanceTask)
async def retrieve_seedance_task(task_id: str):
    try:
        return await SeedanceClient().retrieve_task(task_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Seedance retrieve task failed: {exc}") from exc


@router.delete("/tasks/{task_id}", response_model=SeedanceTask)
async def cancel_seedance_task(task_id: str):
    try:
        return await SeedanceClient().cancel_task(task_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Seedance cancel task failed: {exc}") from exc


@router.get("/health")
async def seedance_health() -> dict[str, object]:
    try:
        config = SeedanceClient().config
        return {
            "provider": "seedance",
            "configured": True,
            "provider_route": config.route,
            "base_url": config.base_url,
            "model": config.model,
            "preferred_video_models": list(config.preferred_video_models),
            "cached_working_model": SeedanceClient._last_working_model,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "provider": "seedance",
            "configured": False,
            "error": str(exc),
        }


@router.post("/vision/chat")
async def seedance_vision_chat(payload: ArkVisionChatRequest) -> dict[str, object]:
    try:
        return ark_chat_completion(
            model=payload.model,
            messages=[build_multimodal_user_message(text=payload.prompt, image_url=str(payload.image_url))],
            max_tokens=payload.max_tokens,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Ark vision chat failed: {exc}") from exc


@router.get("/models/catalog")
async def seedance_model_catalog() -> dict[str, object]:
    try:
        client = SeedanceClient()
        return {
            "provider": "seedance",
            "configured_model": client.config.model,
            "cached_working_model": client._last_working_model,
            "catalog": await client.list_video_models(),
            "candidates": await client._candidate_models(),
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Seedance model catalog failed: {exc}") from exc


@router.post("/models/probe")
async def seedance_model_probe(payload: SeedanceProbeRequest) -> dict[str, object]:
    try:
        client = SeedanceClient()
        results = await client.probe_video_models(stop_on_first_usable=payload.stop_on_first_usable)
        return {
            "provider": "seedance",
            "configured_model": client.config.model,
            "cached_working_model": client._last_working_model,
            "results": results,
            "usable_models": [item for item in results if item.get("classification") == "usable"],
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Seedance model probe failed: {exc}") from exc
