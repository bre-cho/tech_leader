from ai_trading_brain.finance import FinanceOperatingRuntime, FinanceSignalEngine


def sample_rows():
    return [
        {'period': '2026-01', 'channel': 'meta_ads', 'revenue': 10000, 'cash_in': 10000, 'cash_out': 9500, 'ad_spend': 3000, 'cac': 50, 'ltv': 140, 'customers': 120, 'gross_margin': 0.55, 'retention_rate': 0.42, 'planned_budget': 2800, 'actual_budget': 3000},
        {'period': '2026-02', 'channel': 'meta_ads', 'revenue': 9500, 'cash_in': 9500, 'cash_out': 12000, 'ad_spend': 3800, 'cac': 65, 'ltv': 145, 'customers': 110, 'gross_margin': 0.52, 'retention_rate': 0.39, 'planned_budget': 3000, 'actual_budget': 3800},
        {'period': '2026-02', 'channel': 'google_ads', 'revenue': 7000, 'cash_in': 7000, 'cash_out': 5000, 'ad_spend': 1200, 'cac': 32, 'ltv': 160, 'customers': 90, 'gross_margin': 0.58, 'retention_rate': 0.46, 'planned_budget': 1200, 'actual_budget': 1200},
    ]


def test_finance_signal_engine_computes_core_metrics():
    snapshot = FinanceSignalEngine().from_rows(sample_rows(), company_id='acme', cash_balance=10000)
    assert snapshot.company_id == 'acme'
    assert snapshot.total_revenue == 26500
    assert snapshot.signals['runway_months'] > 0
    assert snapshot.signals['ltv_cac_ratio'] > 0


def test_finance_runtime_detects_bottlenecks_and_budget_actions(tmp_path):
    report = FinanceOperatingRuntime(memory_path=tmp_path / 'memory.jsonl').run_rows(sample_rows(), company_id='acme', cash_balance=3000)
    codes = {d.code for d in report.diagnoses}
    assert 'growth_efficiency_collapse' in codes or 'budget_variance_drift' in codes or 'runway_risk' in codes
    assert report.capital_efficiency.score >= 0
    assert report.budget_recommendations
    assert report.ai_ceo_decision['mode'] in {'cash_protection', 'controlled_growth', 'optimize_before_scale', 'hold_and_learn'}
    assert (tmp_path / 'memory.jsonl').exists()


def test_scenario_simulator_outputs_default_scenarios(tmp_path):
    report = FinanceOperatingRuntime(memory_path=tmp_path / 'memory.jsonl').run_rows(sample_rows(), company_id='acme', cash_balance=15000)
    names = {s.name for s in report.scenarios}
    assert 'increase_ads_30_percent' in names
    assert 'revenue_down_15_percent' in names
    assert all(s.recommended_action for s in report.scenarios)
