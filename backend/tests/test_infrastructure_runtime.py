from app.runtime.execution_manager import InfrastructureExecutionManager

def test_infrastructure_runtime_mock():
    req = {
        "business_goal": "launch premium serum ad",
        "industry": "beauty",
        "product_or_service": "glass serum bottle",
        "audience": "women 22-35 interested in skincare",
        "platform": "tiktok_ads",
        "campaign_type": "commercial_visual",
        "brand_context": {},
        "constraints": {"provider": "mock"},
        "requested_outputs": ["poster", "storyboard", "video_concept"],
    }
    res = InfrastructureExecutionManager().run(req)
    assert res["verification"]["passed"] is True
    assert res["promotion_gate"]["status"] in ["PROMOTED", "CANDIDATE"]
    assert res["execution_result"]["commercial_reasoning"]["commercial_reasoning_score"] >= 80
    assert res["artifacts"][0]["checksum"]
