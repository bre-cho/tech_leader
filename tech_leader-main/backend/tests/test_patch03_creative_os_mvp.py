from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_patch03_creative_os_run():
    payload = {
        "brand": {
            "brand_name": "AURA",
            "industry": "beauty",
            "product_name": "Glow Serum",
            "product_type": "serum",
            "audience": "Vietnamese women 22-35",
            "channel": "TikTok ads",
            "objective": "conversion",
        },
        "brief": "Luxury skincare advertising poster with KOL face, serum foreground, warm gold lighting.",
        "campaign_type": "commercial_visual",
        "output_targets": ["social", "poster"],
        "save_memory": True,
    }

    res = client.post("/api/v1/creative-os/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["completed", "blocked"]
    assert data["run_id"]
    assert isinstance(data.get("artifacts", []), list)
