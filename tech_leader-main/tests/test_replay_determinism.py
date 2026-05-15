from ai_trading_brain.graphs.dependency_evolution_graph import DependencyEvolutionGraph
def test_dependency_snapshot_deterministic_shape():
    r=DependencyEvolutionGraph('.').snapshot()
    assert 'graph_hash' in r and r['node_count'] > 0
