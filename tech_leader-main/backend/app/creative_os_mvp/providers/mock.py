from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from app.creative_os_mvp.providers.base import RenderProvider
from app.creative_os_mvp.models.schemas import CreativeRequest

class MockCommercialProvider(RenderProvider):
    def generate(self, prompt: str, negative_prompt: str, req: CreativeRequest) -> bytes:
        w,h=(1080,1350) if req.aspect_ratio=="4:5" else (1280,720)
        img=Image.new("RGB",(w,h),(18,18,24))
        d=ImageDraw.Draw(img)
        brand=req.brand.brand_name or "AI Creative OS"
        product=req.brand.product_name or req.brand.product_type or "Product"
        d.rectangle([40,40,w-40,h-40], outline=(220,190,110), width=4)
        d.text((70,80), brand[:40], fill=(245,230,190))
        d.text((70,130), product[:50], fill=(255,255,255))
        d.text((70,200), "COMMERCIAL VISUAL REASONING", fill=(140,200,255))
        lines=["Attention → Product Hero → Trust → CTA", "Typography-safe commercial layout", "Mock provider artifact for dev/CI"]
        y=280
        for line in lines:
            d.text((70,y), line, fill=(220,220,230)); y+=50
        buf=BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()
