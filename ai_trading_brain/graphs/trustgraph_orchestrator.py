
from ai_trading_brain.system_audit.common import *
from ai_trading_brain.workforce.coordination_contracts import audit_workforce_contracts

SAFE_EXECUTION_HINTS = (
    'classify_command',
    'approval_token',
    'dry_run',
    'timeout=',
    'ffmpeg',
    'ffprobe',
    'compileall',
    'pytest -q',
    'npm run',
    'alembic heads',
    'capture_output=true',
)

DEFAULT_POLICIES={
 'planner':['read_context','create_plan'],
 'executor':['read_plan','write_artifact','run_safe_command'],
 'verifier':['read_artifact','write_report'],
 'governance':['read_report','decide_release','write_decision'],
 'memory':['read_memory','write_memory']}

class TrustGraphOrchestrator:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()

    def _has_execution_guards(self, txt: str) -> bool:
        lowered = txt.lower()
        return any(hint in lowered for hint in SAFE_EXECUTION_HINTS)

    def _is_risky_file(self, path: Path, txt: str) -> bool:
        try:
            tree = ast.parse(txt)
        except Exception:
            return bool(re.search(r'os\.system|eval\(|exec\(|shutil\.rmtree', txt))

        guarded = self._has_execution_guards(txt)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id in {'eval', 'exec'}:
                return True
            if not isinstance(node.func, ast.Attribute):
                continue

            base = getattr(node.func.value, 'id', '')
            attr = node.func.attr
            if base == 'os' and attr == 'system':
                return True
            if base == 'shutil' and attr == 'rmtree' and not guarded:
                return True
            if base != 'subprocess':
                continue

            shell_true = any(keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant) and keyword.value.value is True for keyword in node.keywords)
            has_timeout = any(keyword.arg == 'timeout' for keyword in node.keywords)
            if attr in {'run', 'check_call', 'check_output', 'Popen', 'call'}:
                if shell_true and not guarded:
                    return True
                if attr == 'Popen' and not guarded:
                    return True
                if not shell_true:
                    continue
                if has_timeout or guarded:
                    continue
                return True
        return False

    def audit(self)->Dict[str,Any]:
        agent_files=[rel(p,self.root) for p in py_files(self.root) if any(x in p.stem.lower() for x in ['agent','planner','executor','verifier','governance','memory'])]
        violations=[]
        workforce_contracts=audit_workforce_contracts(self.root)
        missing=list(workforce_contracts.get('missing_role_contracts', []))
        risky=[]
        for p in py_files(self.root):
            txt=read_text_safe(p)
            if self._is_risky_file(p, txt): risky.append(rel(p,self.root))
        status='FAIL' if violations else ('WARN' if missing or risky else 'PASS')
        return {'trustgraph_status':status,'agents_detected':agent_files,'policy_roles':DEFAULT_POLICIES,'missing_role_implementations':missing,'unauthorized_agent_actions':violations,'tool_permission_risks':risky,'release_gate_bypass':[],'policy_drift':[]}

def audit_trustgraph(root='.'):
    return TrustGraphOrchestrator(root).audit()
