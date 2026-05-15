
from ai_trading_brain.system_audit.common import *
class RevenueIntelligence:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()
    def analyze(self)->Dict[str,Any]:
        terms=['revenue', 'sales', 'ltv', 'roi', 'cashflow']; hits=[]
        for p in all_code_files(self.root):
            txt=(rel(p,self.root)+' '+read_text_safe(p)).lower()
            if any(t in txt for t in terms): hits.append(rel(p,self.root))
        return {'module':'revenue_intelligence','status':'PASS' if hits else 'WARN','signals_detected':hits[:50],'terms':terms}

def analyze_revenue_intelligence(root='.'):
    return RevenueIntelligence(root).analyze()
