
from ai_trading_brain.system_audit.common import *
from .context_graph_integrity import check_context_graph_integrity

class DependencyEvolutionGraph:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()
    def snapshot(self)->Dict[str,Any]:
        graph=check_context_graph_integrity(self.root)
        snap={'created_at':time.time(),'root':str(self.root),'node_count':graph['nodes_count'],'edge_count':graph['edges_count'],'graph_hash':hashlib.sha256(json.dumps(graph,sort_keys=True).encode()).hexdigest(),'graph':graph}
        return snap
    def save_snapshot(self, path: str | Path | None=None)->Dict[str,Any]:
        snap=self.snapshot(); out=Path(path) if path else self.root/'docs'/'runtime'/'dependency-evolution-snapshot.json'; write_json(out,snap); return snap

def build_dependency_evolution_snapshot(root='.'):
    return DependencyEvolutionGraph(root).save_snapshot()
