import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai_trading_brain.graphs.context_graph_integrity import check_context_graph_integrity
from ai_trading_brain.graphs.artifact_lineage_graph import audit_artifact_lineage
import argparse,json
p=argparse.ArgumentParser(); p.add_argument('--root',default='.')
a=p.parse_args(); print(json.dumps({'context_graph':check_context_graph_integrity(a.root),'artifact_lineage':audit_artifact_lineage(a.root)},ensure_ascii=False,indent=2))
