import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai_trading_brain.graphs.trustgraph_orchestrator import audit_trustgraph
import argparse,json
p=argparse.ArgumentParser(); p.add_argument('--root',default='.')
a=p.parse_args(); print(json.dumps(audit_trustgraph(a.root),ensure_ascii=False,indent=2))
