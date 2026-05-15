import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai_trading_brain.system_audit.report_builder import build_system_audit_report
import argparse,json,sys
p=argparse.ArgumentParser(); p.add_argument('--root',default='.'); p.add_argument('--heavy',action='store_true')
a=p.parse_args(); r=build_system_audit_report(a.root,a.heavy); print(json.dumps(r['release_gate'],ensure_ascii=False,indent=2)); sys.exit(0 if r['release_gate']['release_status']=='GO' else 1)
