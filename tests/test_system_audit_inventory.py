from ai_trading_brain.system_audit.inventory_detector import run_inventory_detection
def test_inventory_detector_runs():
    r=run_inventory_detection('.')
    assert 'layers' in r and r['status'] in ['PASS','WARN']
