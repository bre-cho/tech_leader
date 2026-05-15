
from .inventory_detector import run_inventory_detection
from .static_scanner import run_static_scan
from .runtime_validator import run_runtime_validation
from ai_trading_brain.graphs.context_graph_integrity import check_context_graph_integrity
from ai_trading_brain.graphs.trustgraph_orchestrator import audit_trustgraph
from ai_trading_brain.graphs.artifact_lineage_graph import audit_artifact_lineage
from ai_trading_brain.memory_governance.memory_topology import audit_memory_topology
from ai_trading_brain.memory_governance.organizational_memory_auditor import audit_organizational_memory
from ai_trading_brain.memory_governance.cross_agent_state import audit_cross_agent_state
from ai_trading_brain.workforce.coordination_contracts import audit_workforce_contracts
from ai_trading_brain.strategic_cognition.economic_flow_auditor import audit_economic_flow

class ArchitectureAuditor:
    def __init__(self, root='.'):
        self.root=root
    def audit(self, run_heavy=False):
        return {'phase':'PHASE 4 — Architecture Audit','inventory':run_inventory_detection(self.root),'static':run_static_scan(self.root),'runtime':run_runtime_validation(self.root, run_heavy=run_heavy),'context_graph':check_context_graph_integrity(self.root),'trustgraph':audit_trustgraph(self.root),'artifact_lineage':audit_artifact_lineage(self.root),'memory_topology':audit_memory_topology(self.root),'organizational_memory':audit_organizational_memory(self.root),'cross_agent_state':audit_cross_agent_state(self.root),'workforce_contracts':audit_workforce_contracts(self.root),'economic_flow':audit_economic_flow(self.root)}

def run_architecture_audit(root='.', run_heavy=False):
    return ArchitectureAuditor(root).audit(run_heavy=run_heavy)
