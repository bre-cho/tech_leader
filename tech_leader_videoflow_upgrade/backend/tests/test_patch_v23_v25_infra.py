from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


def _sample_image_bytes() -> bytes:
    img = Image.new("RGB", (128, 128), color=(180, 140, 120))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_v23_color_intelligence_run_and_graph():
    payload = {
        "brand_name": "PatchBrand",
        "industry": "spa",
        "use_case": "showroom",
        "audience": "premium buyers",
        "desired_perception": ["trust", "luxury", "conversion"],
        "cultural_context": "Vietnam",
    }
    run_res = client.post("/api/v1/color-intelligence/run", json=payload)
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["run_id"].startswith("color_")
    assert len(run_data["palette"]) >= 4

    graph_res = client.get("/api/v1/color-intelligence/graph")
    assert graph_res.status_code == 200
    assert isinstance(graph_res.json().get("items"), list)


def test_v24_blend_retouch_run_and_get():
    files = {"file": ("portrait.jpg", _sample_image_bytes(), "image/jpeg")}
    data = {
        "brand_name": "PatchBrand",
        "use_case": "beauty",
        "preset": "beauty_clean",
        "strength": "0.65",
        "skin_protection": "true",
        "texture_preservation": "true",
        "export_scale": "preview",
    }
    run_res = client.post("/api/v1/blend-retouch/run", files=files, data=data)
    assert run_res.status_code == 200, run_res.text
    run_data = run_res.json()
    assert run_data["run_id"].startswith("blend_")
    assert run_data["qa"]["score"] >= 80

    get_res = client.get(f"/api/v1/blend-retouch/runs/{run_data['run_id']}")
    assert get_res.status_code == 200
    assert get_res.json()["run_id"] == run_data["run_id"]


def test_v25_memory_restoration_run_and_get():
    files = {"file": ("old_photo.jpg", _sample_image_bytes(), "image/jpeg")}
    data = {
        "customer_key": "demo_customer",
        "mode": "restore_colorize_8k",
        "preset": "family_memory",
        "strength": "0.65",
        "face_restore": "true",
        "colorize": "true",
        "natural_asian_skin_tones": "true",
        "print_export": "true",
        "export_scale": "preview",
    }
    run_res = client.post("/api/v1/memory-restoration/run", files=files, data=data)
    assert run_res.status_code == 200, run_res.text
    run_data = run_res.json()
    assert run_data["run_id"].startswith("restore_")
    assert run_data["qa"]["identity_safe"] is True

    get_res = client.get(f"/api/v1/memory-restoration/runs/{run_data['run_id']}")
    assert get_res.status_code == 200
    assert get_res.json()["run_id"] == run_data["run_id"]
