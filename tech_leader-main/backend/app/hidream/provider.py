
from __future__ import annotations
import base64, io, os, random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import requests
from PIL import Image, ImageDraw, ImageFont
from app.config import settings
from app.schemas.hidream import HiDreamPromptContract, HiDreamGenerateRequest

class HiDreamProviderError(RuntimeError):
    pass

class BaseHiDreamProvider(ABC):
    provider_name = "base"
    @abstractmethod
    def generate(self, req: HiDreamGenerateRequest, contract: HiDreamPromptContract) -> bytes:
        raise NotImplementedError

class MockHiDreamProvider(BaseHiDreamProvider):
    """Deterministic operational mock that creates a real PNG artifact for CI/dev without GPU."""
    provider_name = "mock"
    def generate(self, req, contract) -> bytes:
        w, h = [int(x) for x in contract.provider_params.get("size", "1024x1280").split("x")]
        seed = req.seed if req.seed is not None else abs(hash(contract.positive_prompt)) % 100000
        rnd = random.Random(seed)
        img = Image.new("RGB", (w, h), (18, 18, 22))
        draw = ImageDraw.Draw(img)
        # luxury gradient bands
        for y in range(h):
            r = int(18 + 35 * y / h)
            g = int(18 + 20 * y / h)
            b = int(22 + 45 * y / h)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        # product/model placeholder composition, deterministic but actual image file
        accent = (220, 178, 104)
        draw.ellipse((w*0.18, h*0.10, w*0.82, h*0.68), outline=accent, width=max(3, w//200))
        draw.rounded_rectangle((w*0.58, h*0.38, w*0.78, h*0.78), radius=20, fill=(235, 215, 185), outline=(255,245,220), width=3)
        draw.rectangle((w*0.62, h*0.42, w*0.74, h*0.56), fill=(40, 34, 38))
        draw.text((w*0.08, h*0.05), "HiDream V27 Preview", fill=(245,245,245))
        draw.text((w*0.08, h*0.09), req.product_name[:40], fill=accent)
        draw.text((w*0.08, h*0.13), req.use_case, fill=(220,220,230))
        # faux detail dots
        for _ in range(450):
            x, y = rnd.randrange(w), rnd.randrange(h)
            c = rnd.randrange(60, 255)
            img.putpixel((x, y), (c, max(0, c-30), max(0, c-70)))
        buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()

class HFInferenceHiDreamProvider(BaseHiDreamProvider):
    provider_name = "hf_inference"
    def generate(self, req, contract) -> bytes:
        token = settings.hidream_hf_token
        if not token:
            raise HiDreamProviderError("HUGGINGFACE_TOKEN is required for HIDREAM_PROVIDER=hf_inference")
        url = f"https://api-inference.huggingface.co/models/{settings.hidream_model_id}"
        payload = {
            "inputs": contract.positive_prompt,
            "parameters": {
                "negative_prompt": contract.negative_prompt,
                "num_inference_steps": contract.provider_params.get("num_inference_steps"),
                "guidance_scale": contract.provider_params.get("guidance_scale"),
                "seed": contract.provider_params.get("seed"),
            }
        }
        resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=settings.hidream_timeout_seconds)
        if resp.status_code >= 400:
            raise HiDreamProviderError(f"HF inference failed {resp.status_code}: {resp.text[:500]}")
        ctype = resp.headers.get("content-type", "")
        if "image" not in ctype and not resp.content.startswith(b"\x89PNG") and not resp.content.startswith(b"\xff\xd8"):
            raise HiDreamProviderError(f"HF response is not an image: {resp.text[:500]}")
        return resp.content

class LocalDiffusersHiDreamProvider(BaseHiDreamProvider):
    provider_name = "local_diffusers"
    def generate(self, req, contract) -> bytes:
        try:
            import torch
            from diffusers import AutoPipelineForText2Image
        except Exception as e:
            raise HiDreamProviderError("Install torch + diffusers for HIDREAM_PROVIDER=local_diffusers") from e
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        pipe = AutoPipelineForText2Image.from_pretrained(settings.hidream_model_id, torch_dtype=dtype)
        pipe = pipe.to(device)
        params = contract.provider_params
        width, height = [int(x) for x in params.get("size", "1024x1280").split("x")]
        generator = torch.Generator(device=device)
        if params.get("seed") is not None:
            generator = generator.manual_seed(int(params["seed"]))
        image = pipe(
            prompt=contract.positive_prompt,
            negative_prompt=contract.negative_prompt,
            width=width,
            height=height,
            num_inference_steps=int(params.get("num_inference_steps", 36)),
            guidance_scale=float(params.get("guidance_scale", 5.5)),
            generator=generator,
        ).images[0]
        buf = io.BytesIO(); image.save(buf, format="PNG"); return buf.getvalue()

def get_provider(mode: Optional[str] = None) -> BaseHiDreamProvider:
    selected = mode or settings.hidream_provider
    if selected == "mock": return MockHiDreamProvider()
    if selected == "hf_inference": return HFInferenceHiDreamProvider()
    if selected == "local_diffusers": return LocalDiffusersHiDreamProvider()
    raise HiDreamProviderError(f"Unknown HiDream provider: {selected}")
