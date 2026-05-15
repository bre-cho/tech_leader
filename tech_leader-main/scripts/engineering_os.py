#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from ai_trading_brain.engineering_os import build_context_graph, create_phase_plan, evaluate_phase_plan, run_engineering_os, run_verification


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Engineering Operating System CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("graph")
    g.add_argument("--repo", default=".")
    g.add_argument("--out", default="docs/runtime/context-graph.json")
    p = sub.add_parser("plan")
    p.add_argument("task")
    p.add_argument("--repo", default=".")
    p.add_argument("--out", default="docs/runtime/phase-plan.md")
    gate = sub.add_parser("gate")
    gate.add_argument("task")
    gate.add_argument("--repo", default=".")
    v = sub.add_parser("verify")
    v.add_argument("task")
    v.add_argument("--repo", default=".")
    r = sub.add_parser("run")
    r.add_argument("task")
    r.add_argument("--repo", default=".")
    r.add_argument("--no-verify", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if args.cmd == "graph":
        graph = build_context_graph(repo)
        out = graph.write_json(repo / args.out)
        print(json.dumps({"out": str(out), "stats": graph.stats}, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "plan":
        plan = create_phase_plan(args.task, repo)
        out = repo / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(plan.to_markdown(), encoding="utf-8")
        print(str(out))
        return 0
    if args.cmd == "gate":
        plan = create_phase_plan(args.task, repo)
        print(json.dumps(evaluate_phase_plan(plan).to_dict(), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "verify":
        report = run_verification(args.task, repo)
        print(report.to_markdown())
        return 0 if report.passed else 1
    if args.cmd == "run":
        result = run_engineering_os(args.task, repo, verify=not args.no_verify)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
