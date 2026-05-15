#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai_trading_brain.knowledge_os import KnowledgeOSRuntime


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent 16 Knowledge OS - local-first hybrid search + memory runtime")
    parser.add_argument("command", choices=["index", "ask", "remember", "recall"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--db", default=".knowledge_os/knowledge.sqlite")
    parser.add_argument("--query", default="")
    parser.add_argument("--content", default="")
    parser.add_argument("--kind", default=None)
    parser.add_argument("--score", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    runtime = KnowledgeOSRuntime(args.db)
    if args.command == "index":
        result = runtime.build_index(args.root, reset=True)
    elif args.command == "ask":
        if not args.query:
            raise SystemExit("--query is required for ask")
        result = runtime.query(args.query, limit=args.limit)
    elif args.command == "remember":
        if not args.content:
            raise SystemExit("--content is required for remember")
        result = runtime.remember_winner(args.content, score=args.score, kind=args.kind or "winner_pattern")
    else:
        result = runtime.recall(kind=args.kind, limit=args.limit)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
