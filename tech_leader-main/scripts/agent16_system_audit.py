import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai_trading_brain.system_audit.report_builder import build_system_audit_report
import argparse, json
p=argparse.ArgumentParser(); p.add_argument('--root',default='.'); p.add_argument('--heavy',action='store_true'); p.add_argument('--output')
a=p.parse_args(); r=build_system_audit_report(a.root,a.heavy,a.output); print(json.dumps(r['executive_summary'],ensure_ascii=False,indent=2))
