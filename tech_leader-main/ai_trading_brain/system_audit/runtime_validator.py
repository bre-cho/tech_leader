from .common import *
import subprocess

class RuntimeValidator:
    def __init__(self, root: str | Path='.'):
        self.root = Path(root).resolve()

    def validate(self, run_heavy: bool = False) -> Dict[str, Any]:
        checks = []
        def cmd(name, args, timeout=60):
            try:
                r = subprocess.run(args, cwd=self.root, text=True, capture_output=True, timeout=timeout)
                checks.append({'name': name, 'ok': r.returncode == 0, 'returncode': r.returncode, 'stdout': r.stdout[-2000:], 'stderr': r.stderr[-2000:]})
            except Exception as e:
                checks.append({'name': name, 'ok': False, 'error': str(e)})
        cmd('python_compile', ['python', '-m', 'compileall', '-q', 'ai_trading_brain', 'scripts'])
        # Heavy checks are opt-in to avoid recursive pytest calls when report_builder is tested.
        if run_heavy and (self.root / 'tests').exists():
            cmd('pytest', ['python', '-m', 'pytest', '-q'], timeout=120)
        if run_heavy and (self.root / 'package.json').exists():
            cmd('npm_build', ['npm', 'run', 'build'], timeout=120)
        if run_heavy and (self.root / 'alembic.ini').exists():
            cmd('alembic_heads', ['alembic', 'heads'], timeout=60)
        status = 'PASS' if all(c.get('ok') for c in checks) else 'FAIL'
        return {'phase': 'PHASE 3 — Runtime Validation', 'status': status, 'checks': checks}

def run_runtime_validation(root='.', run_heavy=False):
    return RuntimeValidator(root).validate(run_heavy=run_heavy)
