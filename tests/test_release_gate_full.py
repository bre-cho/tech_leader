from ai_trading_brain.system_audit.report_builder import build_system_audit_report
def test_release_gate_report_runs():
    r=build_system_audit_report('.')
    assert r['release_gate']['release_status'] in ['GO','NO-GO']
