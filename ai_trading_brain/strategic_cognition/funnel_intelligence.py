
from ai_trading_brain.system_audit.common import *
class FunnelIntelligence:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()
    def analyze(self)->Dict[str,Any]:
        terms=['funnel', 'conversion', 'lead', 'checkout', 'retention']; hits=[]
        for p in all_code_files(self.root):
            txt=(rel(p,self.root)+' '+read_text_safe(p)).lower()
            if any(t in txt for t in terms): hits.append(rel(p,self.root))
        return {'module':'funnel_intelligence','status':'PASS' if hits else 'WARN','signals_detected':hits[:50],'terms':terms}

def analyze_funnel_intelligence(root='.'):
    return FunnelIntelligence(root).analyze()
