from ai_trading_brain.architecture_observer import ArchitectureObserverRuntime

def test_architecture_observer_runs(tmp_path):
    report = ArchitectureObserverRuntime('.').run(['ai_trading_brain/knowledge_os/runtime.py'], tmp_path / 'arch.json')
    assert report.blast_radius.risk_level in {'low','medium','high','critical'}
    assert report.dependency_evolution.nodes
