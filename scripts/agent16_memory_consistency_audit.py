import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai_trading_brain.memory_governance.memory_topology import audit_memory_topology
from ai_trading_brain.memory_governance.organizational_memory_auditor import audit_organizational_memory
from ai_trading_brain.memory_governance.cross_agent_state import audit_cross_agent_state
import argparse,json
p=argparse.ArgumentParser(); p.add_argument('--root',default='.')
a=p.parse_args(); print(json.dumps({'topology':audit_memory_topology(a.root),'organization':audit_organizational_memory(a.root),'state':audit_cross_agent_state(a.root)},ensure_ascii=False,indent=2))
