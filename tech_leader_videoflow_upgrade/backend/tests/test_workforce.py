from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_image_design_workforce_runs():
    payload = {
        "save_memory": True,
        "brief": {
            "brand_name": "Demo Beauty",
            "industry": "beauty",
            "product_name": "Glow Serum",
            "product_type": "serum bottle",
            "target_audience": "Vietnamese women 22-35",
            "campaign_goal": "conversion",
            "channel": "tiktok",
            "offer": "Try mini serum today",
            "brand_tone": "premium, trustworthy, luxury"
        }
    }
    res = client.post("/api/v1/workforce/image-design/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert len(data["agent_results"]) == 9
    assert data["verification_score"] >= 90
    assert "AI COMMERCIAL DESIGN WORKFORCE OUTPUT" in data["final_prompt"]
    assert data["promotion_status"] == "PROMOTED_TO_WORKFLOW_RUNTIME"
