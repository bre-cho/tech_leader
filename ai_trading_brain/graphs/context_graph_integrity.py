
from ai_trading_brain.system_audit.common import *
import importlib.util
import sys

class ContextGraphIntegrityChecker:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()

    def _module_name(self, path: Path) -> str:
        relative = path.relative_to(self.root)
        parts = list(relative.parts)
        if parts[-1] == '__init__.py':
            return '.'.join(parts[:-1])
        parts[-1] = path.stem
        return '.'.join(parts)

    def _current_package(self, module_name: str, is_package_file: bool) -> str:
        if not module_name:
            return ''
        if is_package_file:
            return module_name
        return module_name.rsplit('.', 1)[0] if '.' in module_name else ''

    def _resolve_import_candidates(self, current_package: str, current_namespace: str, node: ast.AST) -> tuple[list[str], bool]:
        if isinstance(node, ast.Import):
            candidates: list[str] = []
            for alias in node.names:
                candidates.append(alias.name)
                if '.' not in alias.name and current_package:
                    candidates.append(f'{current_package}.{alias.name}')
                if '.' not in alias.name and current_namespace and current_namespace != current_package:
                    candidates.append(f'{current_namespace}.{alias.name}')
            return candidates, False

        if not isinstance(node, ast.ImportFrom):
            return [], False

        local_required = node.level > 0
        base_parts = current_package.split('.') if local_required and current_package else []
        if local_required and node.level > 1:
            trim = node.level - 1
            base_parts = base_parts[:-trim] if trim <= len(base_parts) else []

        base = '.'.join(part for part in [*base_parts, node.module or ''] if part)
        candidates = []
        if base:
            candidates.append(base)
        elif node.module:
            candidates.append(node.module)
        if not local_required and node.module and '.' not in node.module and current_namespace:
            candidates.append(f'{current_namespace}.{node.module}')
        for alias in node.names:
            if alias.name == '*':
                continue
            if base:
                candidates.append(f'{base}.{alias.name}')
            elif local_required:
                prefix = '.'.join(base_parts)
                candidates.append(f'{prefix}.{alias.name}' if prefix else alias.name)
            else:
                candidates.append(alias.name)
        return candidates, local_required

    def _is_external_module(self, module_name: str) -> bool:
        root_name = module_name.split('.')[0]
        if not root_name:
            return True
        if root_name in sys.builtin_module_names or root_name in getattr(sys, 'stdlib_module_names', set()):
            return True
        try:
            return importlib.util.find_spec(root_name) is not None
        except Exception:
            return False

    def check(self)->Dict[str,Any]:
        files=all_code_files(self.root)
        nodes=[{'id':rel(f,self.root),'hash':file_hash(f)} for f in files]
        edges=[]; broken=[]; cycles=[]
        python_files = py_files(self.root)
        module_index={self._module_name(p):rel(p,self.root) for p in python_files}
        local_roots={module.split('.')[0] for module in module_index if module}
        for f in py_files(self.root):
            txt=read_text_safe(f)
            try: tree=ast.parse(txt)
            except Exception: continue
            current_module = self._module_name(f)
            current_package = self._current_package(current_module, f.name == '__init__.py')
            current_namespace = '.'.join(f.relative_to(self.root).parts[:-1])
            for n in ast.walk(tree):
                candidates, local_required = self._resolve_import_candidates(current_package, current_namespace, n)
                if not candidates:
                    continue
                target = next((candidate for candidate in candidates if candidate in module_index), None)
                if target:
                    edges.append({'from':rel(f,self.root),'to':module_index[target],'type':'python_import'})
                    continue
                first_candidate = next((candidate for candidate in candidates if candidate), None)
                if not first_candidate:
                    continue
                if local_required or first_candidate.split('.')[0] in local_roots:
                    broken.append({'from':rel(f,self.root),'missing_module':first_candidate})
                    continue
                if self._is_external_module(first_candidate):
                    continue
        return {'context_graph_status':'PASS' if not broken else 'WARN','nodes_count':len(nodes),'edges_count':len(edges),'missing_nodes':[],'orphan_nodes':[],'broken_edges':broken[:100],'cyclic_dependencies':cycles,'sample_nodes':nodes[:20],'sample_edges':edges[:50]}

def check_context_graph_integrity(root='.'):
    return ContextGraphIntegrityChecker(root).check()
