#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai_trading_brain.techlead.graph_builder import ContextGraphBuilder

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('repo', nargs='?', default='.')
    p.add_argument('--out', default='context_graph')
    args = p.parse_args()
    graph = ContextGraphBuilder(args.repo).write(args.out)
    print(f"Context graph written to {args.out}: {graph['summary']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
