from ai_trading_brain.graphs.context_graph_integrity import check_context_graph_integrity
def test_context_graph_integrity_runs():
    r=check_context_graph_integrity('.')
    assert r['nodes_count'] > 0
    broken = {edge['missing_module'] for edge in r['broken_edges']}
    assert '__future__' not in broken
    assert 'argparse' not in broken
