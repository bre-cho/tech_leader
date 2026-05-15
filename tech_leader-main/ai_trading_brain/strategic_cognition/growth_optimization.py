
from ai_trading_brain.system_audit.common import *
class GrowthOptimization:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()
    def analyze(self)->Dict[str,Any]:
        terms=['growth', 'experiment', 'winner', 'scale', 'optimize']; hits=[]
        for p in all_code_files(self.root):
            txt=(rel(p,self.root)+' '+read_text_safe(p)).lower()
            if any(t in txt for t in terms): hits.append(rel(p,self.root))
        return {'module':'growth_optimization','status':'PASS' if hits else 'WARN','signals_detected':hits[:50],'terms':terms}

def analyze_growth_optimization(root='.'):
    return GrowthOptimization(root).analyze()
