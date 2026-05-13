from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_patch04_creative_infrastructure_run():
    payload = {
        "provider": "mock",
        "export_targets": ["poster", "tiktok", "landing"],
        "business": {
            "brand_name": "Demo Glow",
            "industry": "beauty",
            "product_name": "Glow Serum",
            "product_type": "serum bottle",
            "audience": "Vietnamese women 22-35",
            "goal": "conversion",
            "channel": "tiktok",
            "offer": "Try mini serum today",
            "reference_notes": "premium beauty, luxury, trustworthy",
        },
    }

    res = client.post("/api/v1/creative-infrastructure/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["operating_law_passed"] is True
    assert len(data["agent_results"]) >= 8
