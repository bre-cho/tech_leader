from ai_trading_brain.graphs.trustgraph_orchestrator import audit_trustgraph
def test_trustgraph_audit_runs():
    r=audit_trustgraph('.')
    assert 'trustgraph_status' in r
    risky = set(r['tool_permission_risks'])
    assert 'ai_trading_brain/system_audit/runtime_validator.py' not in risky
    assert 'backend/app/shared/ffmpeg.py' not in risky
