from ai_trading_brain.autonomous_runtime import AutonomousRuntime

def test_autonomous_runtime_runs(tmp_path):
    report = AutonomousRuntime().run('ship feature', output_path=tmp_path / 'auto.json')
    assert len(report.swarm_plan) == 4
    assert all(r.status == 'completed' for r in report.distributed_results)
