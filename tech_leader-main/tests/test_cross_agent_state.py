from ai_trading_brain.memory_governance.cross_agent_state import audit_cross_agent_state
def test_cross_agent_state_runs():
    r=audit_cross_agent_state('.')
    assert 'state_propagation_status' in r
