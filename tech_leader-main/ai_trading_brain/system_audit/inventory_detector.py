
from .common import *

class InventoryDetector:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()
    def detect(self)->Dict[str,Any]:
        markers={
          'backend':['app','api','routers','fastapi','alembic'],
          'frontend':['package.json','next.config.js','vite.config.ts','src/app'],
          'worker':['celery','worker','tasks'],
          'scripts':['scripts'], 'tests':['tests'], 'docs':['docs'], 'ci':['.github/workflows']}
        paths=[p for p in self.root.rglob('*') if p.exists() and '__pycache__' not in p.parts]
        found={k:[] for k in markers}
        for p in paths:
            s=rel(p,self.root).lower()
            for k, ms in markers.items():
                if any(m in s for m in ms): found[k].append(rel(p,self.root))
        layers={
          'context_graph': self._find(['context_graph','graph_builder','context-graph']),
          'trustgraph': self._find(['trustgraph','trust_graph','permission','policy']),
          'agent_runtime': self._find(['runtime.py','agent','planner','executor','verifier']),
          'orchestration_engine': self._find(['orchestr','workflow','queue','dispatcher','scheduler']),
          'memory_store': self._find(['memory','store','rag','index']),
          'governance_layer': self._find(['governance','release_gate','audit','decision']),
          'observability_stack': self._find(['metrics','trace','logging','health']),
          'replay_recovery': self._find(['replay','recovery','rollback','checkpoint','retry']),
        }
        score=sum(1 for v in layers.values() if v['detected'])
        return {'phase':'PHASE 1 — Inventory & Runtime Graph Detection','root':str(self.root),'topology':{k:{'detected':bool(v),'examples':v[:20],'count':len(v)} for k,v in found.items()},'layers':layers,'coverage_score':round(score/max(1,len(layers))*100,2),'status':'PASS' if score>=6 else 'WARN'}
    def _find(self, terms):
        hits=[]
        for p in all_code_files(self.root):
            s=rel(p,self.root).lower()
            if any(t.lower() in s for t in terms): hits.append(rel(p,self.root))
        return {'detected':bool(hits),'count':len(hits),'examples':hits[:25]}

def run_inventory_detection(root='.'):
    return InventoryDetector(root).detect()
