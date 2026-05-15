
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_hidream_commercial_visual_mock_generates_artifact():
    payload = {
        "business_goal": "Create a premium beauty poster that can become a product showcase video",
        "industry": "cosmetic beauty",
        "product_name": "Luminous Serum",
        "audience": "young professional women",
        "use_case": "cosmetic_product",
        "aspect_ratio": "4:5",
        "render_tier": "premium",
        "provider": "mock",
        "brand_dna": {"palette": "champagne gold, ivory, soft black"},
        "visual_dna": {"materials": "glass serum bottle, glowing skin, silk fabric"},
        "campaign_context": {"offer": "launch bundle"}
    }
    r = client.post("/api/v1/hidream/commercial-visual/generate", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "ok"
    assert data["artifact"]["size_bytes"] > 0
    assert data["prompt_contract"]["positive_prompt"]
    assert data["score"]["commercial_score"] >= 0
    assert data["promotion_gate"]["checks"]["workflow_trace_complete"] is True
    assert len(data["storyboard_expansion"]["scenes"]) >= 3
