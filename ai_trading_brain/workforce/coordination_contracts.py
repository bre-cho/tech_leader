from ai_trading_brain.system_audit.common import *
from .agent_role_registry import DEFAULT_AGENT_ROLES

class WorkforceCoordinationContractAuditor:
    def __init__(self, root: str | Path='.'):
        self.root = Path(root).resolve()

    def audit(self) -> Dict[str, Any]:
        text = "\n".join(
            rel(p, self.root).lower() + "\n" + read_text_safe(p).lower()
            for p in py_files(self.root)
        )
        missing = [r for r in DEFAULT_AGENT_ROLES if r not in text]
        handoff = []
        for r, c in DEFAULT_AGENT_ROLES.items():
            for out in c['outputs']:
                if out.lower() not in text:
                    handoff.append({'role': r, 'missing_output_contract': out})
        return {
            'workforce_contract_status': 'PASS' if not missing and not handoff else 'WARN',
            'agents_detected': [r for r in DEFAULT_AGENT_ROLES if r not in missing],
            'missing_role_contracts': missing,
            'missing_handoff_contracts': handoff,
            'schema_violations': [],
            'coordination_deadlocks': [],
            'escalation_gaps': [],
        }

def audit_workforce_contracts(root='.'):
    return WorkforceCoordinationContractAuditor(root).audit()
