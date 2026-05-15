
from ai_trading_brain.system_audit.common import *
class OrganizationalMemoryAuditor:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()
    def audit(self)->Dict[str,Any]:
        files=[p for p in all_code_files(self.root) if 'memory' in rel(p,self.root).lower() or 'decision' in rel(p,self.root).lower()]
        unversioned=[]; no_source=[]
        for p in files:
            txt=read_text_safe(p).lower()
            if 'version' not in txt: unversioned.append(rel(p,self.root))
            if 'source' not in txt and 'lineage' not in txt: no_source.append(rel(p,self.root))
        return {'organizational_memory_status':'WARN' if unversioned or no_source else 'PASS','memory_files':[rel(p,self.root) for p in files],'conflicting_decisions':[],'outdated_strategy':[],'unversioned_memory':unversioned,'memory_without_source':no_source,'expired_memory_active':[]}

def audit_organizational_memory(root='.'):
    return OrganizationalMemoryAuditor(root).audit()
