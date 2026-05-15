import httpx
from app.creative_os_mvp.providers.base import RenderProvider
from app.creative_os_mvp.models.schemas import CreativeRequest
from app.creative_os_mvp.core.config import settings

class HFInferenceProvider(RenderProvider):
    def generate(self, prompt: str, negative_prompt: str, req: CreativeRequest) -> bytes:
        if not settings.hf_endpoint_url or not settings.hf_token:
            raise RuntimeError("CREATIVE_OS_HF_ENDPOINT_URL and CREATIVE_OS_HF_TOKEN are required")
        headers={"Authorization": f"Bearer {settings.hf_token}"}
        payload={"inputs": prompt, "parameters": {"negative_prompt": negative_prompt}}
        with httpx.Client(timeout=180) as client:
            r=client.post(settings.hf_endpoint_url, headers=headers, json=payload)
            r.raise_for_status()
            return r.content
