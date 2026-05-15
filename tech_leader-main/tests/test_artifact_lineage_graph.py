from ai_trading_brain.graphs.artifact_lineage_graph import audit_artifact_lineage
def test_artifact_lineage_runs():
    r=audit_artifact_lineage('.')
    assert 'artifacts_scanned' in r
