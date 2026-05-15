#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_trading_brain.codenomad_core import (
    build_healing_plan,
    create_codenomad_plan,
    run_codenomad_runtime,
    run_command,
    scan_project_context,
    write_context,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent 16 CodeNomad Core CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("context", help="Quét ngữ cảnh dự án")
    c.add_argument("--repo", default=".")
    c.add_argument("--out", default="docs/runtime/codenomad-context.json")

    p = sub.add_parser("plan", help="Tạo kế hoạch thực thi")
    p.add_argument("task")
    p.add_argument("--repo", default=".")
    p.add_argument("--out", default="docs/runtime/codenomad-plan.md")

    x = sub.add_parser("exec", help="Chạy một lệnh qua cổng an toàn")
    x.add_argument("command")
    x.add_argument("--repo", default=".")
    x.add_argument("--execute", action="store_true", help="Tắt dry-run và chạy thật")
    x.add_argument("--approval-token")
    x.add_argument("--timeout", type=int, default=60)

    h = sub.add_parser("heal", help="Tạo kế hoạch tự sửa lỗi từ runtime report")
    h.add_argument("--repo", default=".")
    h.add_argument("--last-report", default="docs/runtime/codenomad-runtime-report.md")
    h.add_argument("--out", default="docs/runtime/codenomad-healing-plan.md")

    r = sub.add_parser("run", help="Chạy vòng lặp plan -> command gate -> report")
    r.add_argument("task")
    r.add_argument("--repo", default=".")
    r.add_argument("--execute", action="store_true", help="Tắt dry-run và chạy thật các command an toàn")
    r.add_argument("--approval-token")
    r.add_argument("--json", action="store_true")

    args = parser.parse_args()
    repo = Path(args.repo).resolve()

    if args.cmd == "context":
        ctx = scan_project_context(repo)
        out = write_context(ctx, repo / args.out)
        print(json.dumps({"out": str(out), "files": len(ctx.files), "languages": ctx.languages}, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "plan":
        plan = create_codenomad_plan(args.task, repo)
        out = repo / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(plan.to_markdown(), encoding="utf-8")
        print(str(out))
        return 0
    if args.cmd == "exec":
        result = run_command(args.command, repo, dry_run=not args.execute, approval_token=args.approval_token, timeout=args.timeout)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.status in {"executed", "skipped"} and result.return_code in {0, None} else 1
    if args.cmd == "heal":
        content = build_healing_plan(repo / args.last_report)
        out = repo / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print(str(out))
        return 0
    if args.cmd == "run":
        report = run_codenomad_runtime(args.task, repo, dry_run=not args.execute, approval_token=args.approval_token)
        if args.json:
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(report.to_markdown())
        return 0 if report.passed else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
