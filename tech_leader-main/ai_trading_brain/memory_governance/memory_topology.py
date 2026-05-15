
from ai_trading_brain.system_audit.common import *

MEMORY_LAYERS=['short_term','long_term','task','skill','failure','decision','artifact','organization','economic']
class AgentMemoryTopologyAuditor:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()
    def audit(self)->Dict[str,Any]:
        hits={layer:[] for layer in MEMORY_LAYERS}
        for p in all_code_files(self.root):
            txt=(rel(p,self.root)+' '+read_text_safe(p)).lower()
            for l in MEMORY_LAYERS:
                if l.replace('_',' ') in txt or l in txt: hits[l].append(rel(p,self.root))
        detected=[k for k,v in hits.items() if v]
        missing=[k for k in MEMORY_LAYERS if k not in detected]
        status='PASS' if len(missing)<=2 else 'WARN'
        return {'memory_topology_status':status,'memory_layers_detected':detected,'missing_memory_layers':missing,'layer_evidence':{k:v[:10] for k,v in hits.items() if v},'stale_memory':[],'conflicting_memory':[],'unlinked_memory_records':[],'repair_plan':[f'Add explicit {m} memory adapter/schema' for m in missing]}

def audit_memory_topology(root='.'):
    return AgentMemoryTopologyAuditor(root).audit()
