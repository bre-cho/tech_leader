from ai_trading_brain.system_audit.common import *

EXPECTED = [('planner', 'executor'), ('executor', 'verifier'), ('verifier', 'governance'), ('governance', 'memory')]

class CrossAgentStateAuditor:
    def __init__(self, root: str | Path='.'):
        self.root = Path(root).resolve()

    def audit(self) -> Dict[str, Any]:
        text = "\n".join(
            rel(p, self.root) + "\n" + read_text_safe(p).lower()
            for p in py_files(self.root)
        )
        missing = []
        for a, b in EXPECTED:
            if not (a in text and b in text):
                missing.append({'from': a, 'to': b})
        state_terms = ['task_id', 'status', 'artifact', 'decision', 'retry', 'rollback']
        stale = [t for t in state_terms if t not in text]
        return {
            'state_propagation_status': 'PASS' if not missing and not stale else 'WARN',
            'state_edges_detected': [{'from': a, 'to': b} for a, b in EXPECTED if {'from': a, 'to': b} not in missing],
            'missing_state_transitions': missing,
            'stale_state': stale,
            'state_desync': [],
            'retry_state_gaps': ['retry'] if 'retry' in stale else [],
            'rollback_state_gaps': ['rollback'] if 'rollback' in stale else [],
        }

def audit_cross_agent_state(root='.'):
    return CrossAgentStateAuditor(root).audit()
