from ai_trading_brain.workforce.coordination_contracts import audit_workforce_contracts
def test_workforce_contracts_runs():
    r=audit_workforce_contracts('.')
    assert 'workforce_contract_status' in r
