from fastapi import APIRouter, HTTPException

from apps.api.schemas.image_upscale import ImageUpscaleRequest, ImageUpscaleResponse
from packages.provider_adapters.base import ProviderError
from packages.provider_adapters.image_upscale import UpscaleInput, upscale_image

router = APIRouter(prefix="/api/v1/image-upscale", tags=["image-upscale"])


@router.post("", response_model=ImageUpscaleResponse)
async def create_image_upscale_job(payload: ImageUpscaleRequest):
    if not payload.image_url and not payload.image_base64:
        raise HTTPException(status_code=400, detail="Provide image_url or image_base64")
    try:
        result = await upscale_image(UpscaleInput(**payload.model_dump(mode="json")))
        return ImageUpscaleResponse(**result)
    except ProviderError as exc:
        raise HTTPException(status_code=502 if exc.retryable else 400, detail=exc.to_dict()) from exc
