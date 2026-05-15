from ai_trading_brain.memory_governance.memory_topology import audit_memory_topology
def test_memory_topology_runs():
    r=audit_memory_topology('.')
    assert 'memory_layers_detected' in r
