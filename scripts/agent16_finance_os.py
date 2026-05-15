#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai_trading_brain.finance import FinanceOperatingRuntime


def main() -> int:
    parser = argparse.ArgumentParser(description='Run Agent16 Finance Intelligence Layer for AI Business OS.')
    parser.add_argument('input', help='CSV or JSON finance data file')
    parser.add_argument('--company-id', default='default')
    parser.add_argument('--next-budget', type=float, default=None)
    parser.add_argument('--memory', default='.finance-os/financial_memory.jsonl')
    parser.add_argument('--out', default='.finance-os')
    args = parser.parse_args()

    runtime = FinanceOperatingRuntime(memory_path=args.memory)
    report = runtime.run_file(args.input, company_id=args.company_id, next_budget=args.next_budget)
    report.write(args.out)
    print(report.to_markdown())
    return 1 if report.ai_ceo_decision['mode'] == 'cash_protection' else 0


if __name__ == '__main__':
    raise SystemExit(main())
