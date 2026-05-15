from ai_trading_brain.strategic_cognition.economic_flow_auditor import audit_economic_flow
def test_economic_flow_runs():
    r=audit_economic_flow('.')
    assert 'economic_cognition_status' in r
