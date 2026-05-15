#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai_trading_brain.techlead import Agent16Config, TechnicalLeadAgent


def main() -> int:
    parser = argparse.ArgumentParser(description='Run Agent 16 TrustGraph Context Graph audit.')
    parser.add_argument('repo', nargs='?', default='.', help='Repository root')
    parser.add_argument('--runtime', action='store_true', help='Run pytest/build/compile validation when available')
    parser.add_argument('--apply-safe-fixes', action='store_true', help='Apply conservative safe fixes: __init__.py, dirs, whitespace, command files')
    parser.add_argument('--timeout', type=int, default=45)
    parser.add_argument('--out', default='reports/agent16_audit_report.md')
    parser.add_argument('--json-out', default='reports/agent16_audit_report.json')
    args = parser.parse_args()

    agent = TechnicalLeadAgent(args.repo, Agent16Config(runtime=args.runtime, apply_safe_fixes=args.apply_safe_fixes, timeout_seconds=args.timeout))
    report = agent.run()
    report.write_markdown(Path(args.repo) / args.out)
    report.write_json(Path(args.repo) / args.json_out)
    print(report.executive_summary)
    print(f'Markdown report: {args.out}')
    print(f'JSON report: {args.json_out}')
    return 1 if report.release_gate.value == 'NO-GO' else 0

if __name__ == '__main__':
    raise SystemExit(main())
