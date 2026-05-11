from typing import Any, Dict

from fastapi import APIRouter, Depends, Header, Request

from app.auth.dependencies import require_permission
from app.schemas.provider_schema import (
    ProviderCallbackResult,
    ProviderName,
    ProviderOperationRequest,
)
from app.services.provider_routing.provider_registry import provider_registry

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


@router.get("/status")
def provider_status():
    return {
        "providers": [
            provider.status().model_dump(mode="json")
            for provider in provider_registry.all()
        ]
    }


@router.post("/payload-preview")
def provider_payload_preview(request: ProviderOperationRequest):
    provider = provider_registry.get(request.provider)
    return provider.payload_preview(
        operation=request.operation,
        input_data=request.input,
        dry_run=True,
    ).model_dump(mode="json")


@router.post("/execute", dependencies=[Depends(require_permission("execute:provider"))])
def provider_execute(request: ProviderOperationRequest):
    provider = provider_registry.get(request.provider)
    return provider.execute(
        operation=request.operation,
        input_data=request.input,
        dry_run=request.dry_run,
    ).model_dump(mode="json")


@router.post("/callback/{provider_name}")
async def provider_callback(provider_name: ProviderName, request: Request):
    provider = provider_registry.get(provider_name)
    payload: Dict[str, Any] = await request.json()
    result: ProviderCallbackResult = provider.handle_callback(payload, request.headers)
    return result.model_dump(mode="json")
