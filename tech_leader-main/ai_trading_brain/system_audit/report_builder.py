
from .architecture_auditor import run_architecture_audit
from .patch_planner import build_patch_plan
from .release_gate import decide_release
from .common import write_json
from pathlib import Path
import json
class SystemAuditReportBuilder:
    def __init__(self, root='.'):
        self.root=Path(root).resolve()
    def build(self, run_heavy=False, output=None):
        report=run_architecture_audit(self.root, run_heavy=run_heavy)
        report['patch_planning']=build_patch_plan(report)
        report['release_gate']=decide_release(report)
        report['executive_summary']={'release_status':report['release_gate']['release_status'],'blocking_errors':report['release_gate']['blockers'],'top_risks':[i['title'] for i in report['patch_planning']['patch_plan'][:5]]}
        out=Path(output) if output else self.root/'docs'/'runtime'/'agent16-system-audit-report.json'
        write_json(out, report)
        return report

def build_system_audit_report(root='.', run_heavy=False, output=None): return SystemAuditReportBuilder(root).build(run_heavy, output)
