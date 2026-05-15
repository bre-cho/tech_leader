from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_patch06_compound_os_run_and_ingest():
    payload = {
        "brand_name": "Demo Glow",
        "industry": "beauty",
        "campaign_name": "Glow Serum Launch",
        "product_name": "Glow Serum",
        "product_type": "serum bottle",
        "audience": "Vietnamese women 22-35",
        "goal": "conversion",
        "channel": "tiktok",
        "offer": "Try mini serum today",
        "variants": 2,
    }
    res = client.post("/api/v1/compound-os/creative-business-os/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["operating_law_passed"] is True
    assert len(data["variants"]) == 2

    winner = data["winner_dna"]
    metrics = {
        "campaign_id": data["campaign_id"],
        "variant_id": winner["variant_id"],
        "impressions": 10000,
        "clicks": 300,
        "conversions": 35,
        "revenue": 1000,
        "watch_time_rate": 0.5,
    }
    res2 = client.post("/api/v1/compound-os/analytics/ingest", json=metrics)
    assert res2.status_code == 200
    assert "learning" in res2.json()
