
from ai_trading_brain.system_audit.common import *

class ArtifactLineageGraph:
    def __init__(self, root: str | Path='.'):
        self.root=Path(root).resolve()
    def audit(self)->Dict[str,Any]:
        dirs=[self.root/'docs'/'runtime', self.root/'artifacts', self.root/'storage']
        artifacts=[]; missing_lineage=[]; missing_checksum=[]
        for d in dirs:
            if not d.exists(): continue
            for p in d.rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts:
                    rec={'artifact_id':file_hash(p)[:16],'path':rel(p,self.root),'size_bytes':p.stat().st_size,'checksum':file_hash(p)}
                    artifacts.append(rec)
                    txt=read_text_safe(p) if p.suffix in ['.json','.md','.txt','.jsonl'] else ''
                    if not any(k in txt for k in ['source_task_id','source_job_id','agent_id','input_hash','runtime_version']): missing_lineage.append(rec['path'])
                    if not rec['checksum']: missing_checksum.append(rec['path'])
        status='PASS' if not missing_lineage else 'WARN'
        return {'artifact_lineage_status':status,'artifacts_scanned':len(artifacts),'artifacts':artifacts[:100],'missing_lineage':missing_lineage[:100],'missing_checksum':missing_checksum,'unreplayable_artifacts':missing_lineage[:100],'orphan_artifacts':[],'promotion_eligible':[a['path'] for a in artifacts if a['path'] not in missing_lineage][:50]}

def audit_artifact_lineage(root='.'):
    return ArtifactLineageGraph(root).audit()
