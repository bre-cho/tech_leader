from .common import *

PLACEHOLDER_SECRET_MARKERS = (
    'change-me',
    'changeme',
    'dev-internal-secret',
    'placeholder',
    'example',
    'sample',
    'dummy',
    'fake',
    'mock',
    'test-token',
    'your-',
)

class StaticSystemScanner:
    def __init__(self, root: str | Path='.'):
        self.root = Path(root).resolve()

    def _is_placeholder_secret(self, assignment_text: str) -> bool:
        lowered = assignment_text.lower()
        return any(marker in lowered for marker in PLACEHOLDER_SECRET_MARKERS)

    def scan(self) -> Dict[str, Any]:
        syntax = []
        imports = []
        mocks = []
        secrets = []
        weak_defaults = []
        orphan = []
        secret_pattern = re.compile(r"(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}", re.I)
        for f in py_files(self.root):
            txt = read_text_safe(f)
            try:
                tree = ast.parse(txt)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports += [n.name for n in node.names]
                    if isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
            except SyntaxError as e:
                syntax.append({'file': rel(f, self.root), 'line': e.lineno, 'message': e.msg})
            if re.search(r'TODO|FIXME|placeholder|mock_|fake_', txt, re.I):
                mocks.append(rel(f, self.root))
            for match in secret_pattern.finditer(txt):
                if self._is_placeholder_secret(match.group(0)):
                    weak_defaults.append(rel(f, self.root))
                    continue
                secrets.append(rel(f, self.root))
                break
        files = py_files(self.root)
        for f in files:
            name = f.stem
            if name != '__init__' and sum(1 for p in files if name in read_text_safe(p)) <= 1:
                orphan.append(rel(f, self.root))
        blocking_status = 'FAIL' if syntax or secrets else 'PASS'
        advisory = []
        if mocks:
            advisory.append('mock_leakage_candidates')
        if weak_defaults:
            advisory.append('weak_default_secret_candidates')
        return {
            'phase': 'PHASE 2 — Static System Scan',
            'status': blocking_status,
            'syntax_errors': syntax,
            'imports_detected': sorted(set(imports))[:200],
            'mock_leakage_candidates': mocks[:80],
            'secret_drift_candidates': secrets,
            'weak_default_secret_candidates': sorted(set(weak_defaults))[:80],
            'orphan_module_candidates': orphan[:100],
            'files_scanned': len(files),
            'advisory_status': 'WARN' if advisory else 'PASS',
            'advisory_findings': advisory,
        }

def run_static_scan(root='.'):
    return StaticSystemScanner(root).scan()
