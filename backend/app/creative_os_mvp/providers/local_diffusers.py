from app.creative_os_mvp.providers.base import RenderProvider
from app.creative_os_mvp.models.schemas import CreativeRequest

class LocalDiffusersProvider(RenderProvider):
    def generate(self, prompt: str, negative_prompt: str, req: CreativeRequest) -> bytes:
        # Real hook for GPU server. Kept explicit to avoid fake success.
        # Dev can wire HiDream pipeline here after installing model weights.
        raise RuntimeError("local_diffusers provider requires GPU/model setup. Use mock or hf_inference until configured.")
