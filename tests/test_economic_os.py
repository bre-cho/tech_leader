from ai_trading_brain.economic_os import EconomicOSRuntime
from ai_trading_brain.economic_os.models import EconomicInput

def test_economic_os_runs(tmp_path):
    report = EconomicOSRuntime().run(EconomicInput(1000, 1000, 100, 10, 200), tmp_path / 'eco.json')
    assert report.revenue_intelligence['roas'] == 5.0
    assert report.funnel_intelligence['primary_bottleneck']
