#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai_trading_brain.techlead.agent16 import Agent16Config, TechnicalLeadAgent
from ai_trading_brain.techlead.business_operating import BusinessOperatingMind


def main() -> int:
    parser = argparse.ArgumentParser(description='Run Agent16 Business Operating Mind runtime.')
    parser.add_argument('repo', nargs='?', default='.', help='Repository root')
    parser.add_argument('--runtime', action='store_true', help='Run base Agent16 runtime validation before Business OS reasoning')
    parser.add_argument('--apply-safe-fixes', action='store_true', help='Apply conservative base Agent16 safe fixes first')
    parser.add_argument('--out', default='.agent16-business-os', help='Output directory')
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    base_report = TechnicalLeadAgent(root, Agent16Config(runtime=args.runtime, apply_safe_fixes=args.apply_safe_fixes)).run()
    business_report = BusinessOperatingMind(root).run(base_report.findings, {'summary': base_report.graph})
    business_report.write(root / args.out)
    print(business_report.to_markdown())
    return 1 if business_report.release_gate.value == 'NO-GO' else 0


if __name__ == '__main__':
    raise SystemExit(main())
