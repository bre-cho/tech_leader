#!/usr/bin/env python3
"""
run_full_audit.py — Full audit pipeline orchestrator.

Phases:
  1. Inventory   → docs/audit_reports/inventory.json
  2. Static scan → docs/audit_reports/static_scan.json
  3. Runtime audit via backend API → docs/audit_reports/runtime_audit.json
  4. Aggregate → docs/audit_reports/FULL_AUDIT_REPORT.json
  5. Executive summary → docs/audit_reports/EXECUTIVE_SUMMARY.md

Usage:
    python scripts/run_full_audit.py [--repo-root <path>] [--api-base <url>]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_phase(label: str, cmd: list[str]) -> dict:
    print(f"\n=== Phase: {label} ===")
    result = subprocess.run(cmd, capture_output=True, text=True)
    ok = result.returncode == 0
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return {"phase": label, "passed": ok, "stdout": result.stdout, "stderr": result.stderr}


def try_api_audit(api_base: str) -> dict:
    try:
        import urllib.request
        url = f"{api_base}/api/v1/audit/run"
        req = urllib.request.Request(url, method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e), "note": "backend not reachable; runtime audit skipped"}


def build_executive_summary(report: dict) -> str:
    ts = report.get("generated_at", "unknown")
    gate = report.get("release_gate_status", "UNKNOWN")
    score = report.get("overall_health_score", 0.0)
    blocking = report.get("blocking_failures", [])
    warnings = report.get("warnings", [])

    lines = [
        "# Executive Audit Summary",
        f"\n**Generated:** {ts}",
        f"**Release Gate:** `{gate}`",
        f"**Health Score:** {score:.0%}",
        "",
        "## Blocking Failures" if blocking else "",
        *([f"- {b}" for b in blocking] if blocking else ["*(none)*"]),
        "",
        "## Warnings",
        *([f"- {w}" for w in warnings] if warnings else ["*(none)*"]),
        "",
        "## Phases",
        *[f"- **{p['phase']}**: {'PASS ✅' if p['passed'] else 'FAIL ❌'}" for p in report.get("phases", [])],
    ]
    return "\n".join(l for l in lines if l is not None)


def main():
    parser = argparse.ArgumentParser(description="Full audit pipeline")
    parser.add_argument("--repo-root", default=".", help="Path to repository root")
    parser.add_argument("--api-base", default="http://localhost:8000", help="Backend API base URL")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    python = sys.executable

    phases = []

    # Phase 1: Inventory
    phases.append(run_phase(
        "inventory",
        [python, str(repo_root / "scripts" / "audit_inventory.py"), "--repo-root", str(repo_root)],
    ))

    # Phase 2: Static scan
    phases.append(run_phase(
        "static_scan",
        [python, str(repo_root / "scripts" / "audit_static_scan.py"), "--repo-root", str(repo_root)],
    ))

    # Phase 3: Runtime audit (best-effort — requires running backend)
    runtime_result = try_api_audit(args.api_base)
    phases.append({
        "phase": "runtime_audit",
        "passed": "error" not in runtime_result,
        "result": runtime_result,
    })

    # Load sub-reports
    audit_dir = repo_root / "docs" / "audit_reports"

    def load_json(name: str) -> dict:
        p = audit_dir / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

    inventory = load_json("inventory.json")
    static_scan = load_json("static_scan.json")

    # Determine gate
    blocking_failures = []
    warnings_list = []
    for phase in phases:
        if not phase["passed"]:
            if phase["phase"] in ("inventory", "static_scan"):
                blocking_failures.append(f"{phase['phase']} failed")
            else:
                warnings_list.append(f"{phase['phase']} failed")

    # Add runtime gate from API if available
    rg = runtime_result.get("release_gate", {})
    if rg.get("status") == "NO-GO":
        blocking_failures.extend(rg.get("blocking_failures", []))

    gate = "NO-GO" if blocking_failures else "GO"
    total_phases = len(phases)
    passing = sum(1 for p in phases if p["passed"])
    health_score = round(passing / total_phases, 4)

    full_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_gate_status": gate,
        "overall_health_score": health_score,
        "blocking_failures": blocking_failures,
        "warnings": warnings_list,
        "phases": phases,
        "inventory": inventory,
        "static_scan": static_scan,
        "runtime_audit": runtime_result,
    }

    # Write reports
    audit_dir.mkdir(parents=True, exist_ok=True)
    (audit_dir / "FULL_AUDIT_REPORT.json").write_text(
        json.dumps(full_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (audit_dir / "EXECUTIVE_SUMMARY.md").write_text(
        build_executive_summary(full_report), encoding="utf-8"
    )

    print(f"\n✅ Full audit complete. Gate: {gate}. Score: {health_score:.0%}")
    print(f"Reports: {audit_dir}")

    if gate == "NO-GO":
        sys.exit(1)


if __name__ == "__main__":
    main()
