import base64
import io
from PIL import Image
from fastapi.testclient import TestClient

from apps.api.main import app


def _sample_png_base64() -> str:
    image = Image.new("RGB", (64, 48), color=(180, 120, 40))
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def test_image_upscale_local_contract(monkeypatch, tmp_path):
    from apps.api.core import config
    import packages.provider_adapters.image_upscale as adapter

    monkeypatch.setattr(config.settings, "storage_dir", str(tmp_path))
    monkeypatch.setattr(adapter.settings, "storage_dir", str(tmp_path))
    monkeypatch.setattr(config.settings, "image_upscale_default_provider", "local")
    monkeypatch.setattr(adapter.settings, "image_upscale_default_provider", "local")

    client = TestClient(app)
    response = client.post(
        "/api/v1/image-upscale",
        json={
            "image_base64": _sample_png_base64(),
            "filename": "sample.png",
            "target": "HD",
            "provider": "local",
            "category": "poster",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "succeeded"
    assert data["provider"] == "local"
    assert data["target"] == "HD"
    assert data["width"] >= 64
    assert data["height"] >= 48
    assert data["checksum"]
    assert data["output_url"].startswith("file://")
