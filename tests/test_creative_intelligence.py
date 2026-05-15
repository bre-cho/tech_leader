from ai_trading_brain.creative_intelligence import CreativeIntelligenceRuntime
from ai_trading_brain.creative_intelligence.models import CreativeAsset

def test_creative_runtime_runs(tmp_path):
    asset = CreativeAsset('a1','Title','Secret hook','founders','template offer','luxury proof style')
    report = CreativeIntelligenceRuntime().run(asset, tmp_path / 'creative.json')
    assert report.score.total > 0
    assert len(report.storyboard_memory) == 4
