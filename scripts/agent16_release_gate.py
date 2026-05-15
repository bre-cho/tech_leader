#!/usr/bin/env python
from __future__ import annotations

import argparse, json
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('report', nargs='?', default='reports/agent16_audit_report.json')
    args = p.parse_args()
    data = json.loads(Path(args.report).read_text(encoding='utf-8'))
    gate = data.get('release_gate')
    print(f'Release gate: {gate}')
    return 0 if gate == 'GO' else 1

if __name__ == '__main__':
    raise SystemExit(main())
