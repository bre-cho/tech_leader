from typing import Literal
from pydantic import BaseModel, Field, HttpUrl

UpscaleTarget = Literal["HD", "4K", "8K"]
UpscaleProvider = Literal["auto", "local", "claid", "picwish", "pixelcut"]
ImageCategory = Literal["auto", "poster", "portrait", "product", "ai_art", "text_logo", "old_photo"]


class ImageUpscaleRequest(BaseModel):
    image_url: HttpUrl | None = Field(default=None, description="Publicly reachable source image URL")
    image_base64: str | None = Field(default=None, description="Raw base64 image payload; data URLs are accepted")
    filename: str | None = Field(default=None, description="Optional filename hint when using base64")
    target: UpscaleTarget = "4K"
    provider: UpscaleProvider = "auto"
    category: ImageCategory = "auto"
    denoise: bool = True
    sharpen: bool = True
    face_restore: bool = False
    preserve_text: bool = True
    wait: bool = True


class ImageUpscaleResponse(BaseModel):
    job_id: str
    status: Literal["succeeded", "processing", "failed"]
    provider: str
    target: UpscaleTarget
    scale_factor: int
    width: int | None = None
    height: int | None = None
    output_url: str | None = None
    storage_key: str | None = None
    checksum: str | None = None
    metadata: dict = Field(default_factory=dict)
