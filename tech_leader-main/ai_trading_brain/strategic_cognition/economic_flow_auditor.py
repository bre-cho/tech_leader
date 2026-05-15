from ai_trading_brain.system_audit.common import *
from .revenue_intelligence import analyze_revenue_intelligence
from .traffic_intelligence import analyze_traffic_intelligence
from .funnel_intelligence import analyze_funnel_intelligence
from .growth_optimization import analyze_growth_optimization

class EconomicFlowAuditor:
    def __init__(self, root: str | Path='.'):
        self.root = Path(root).resolve()

    def audit(self) -> Dict[str, Any]:
        modules = [
            analyze_revenue_intelligence(self.root),
            analyze_traffic_intelligence(self.root),
            analyze_funnel_intelligence(self.root),
            analyze_growth_optimization(self.root),
        ]
        missing = [m['module'] for m in modules if m['status'] != 'PASS']
        text = "\n".join(read_text_safe(p).lower() for p in all_code_files(self.root))
        objectives = [x for x in ['revenue', 'traffic', 'funnel', 'growth', 'strategy', 'roi'] if x in text]
        return {
            'economic_cognition_status': 'PASS' if not missing else 'WARN',
            'business_objectives_detected': objectives,
            'unmapped_tasks': [],
            'missing_revenue_flow': ['revenue_intelligence'] if 'revenue_intelligence' in missing else [],
            'missing_growth_loop': ['growth_optimization'] if 'growth_optimization' in missing else [],
            'strategic_blindspots': missing,
            'modules': modules,
            'recommended_priorities': [f'Add explicit {m} contract and runtime metrics' for m in missing],
        }

def audit_economic_flow(root='.'):
    return EconomicFlowAuditor(root).audit()
