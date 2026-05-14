#!/usr/bin/env python3
"""
audit_inventory.py — Phase 1: Runtime topology detection.

Scans the repository and produces docs/audit_reports/inventory.json
describing all detected modules: backend, frontend, workers, scripts,
tests, docs, CI/CD, context graph, trust graph, orchestration, memory,
governance, observability, replay.

Usage:
    python scripts/audit_inventory.py [--repo-root <path>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def _exists(root: Path, *paths: str) -> bool:
    return any((root / p).exists() for p in paths)


def _count_files(directory: Path, glob: str = "**/*.py") -> int:
    if not directory.exists():
        return 0
    return len(list(directory.glob(glob)))


def detect_topology(repo_root: Path) -> dict:
    backend = repo_root / "backend" / "app"
    frontend = repo_root / "frontend"
    scripts = repo_root / "scripts"
    tests_root = repo_root / "tests"
    docs = repo_root / "docs"
    github = repo_root / ".github"

    return {
        "backend": {
            "detected": backend.exists(),
            "python_files": _count_files(backend),
            "has_api": (backend / "api").exists(),
            "has_runtime": (backend / "runtime").exists(),
            "has_governance": (backend / "governance").exists(),
            "has_memory": (backend / "memory").exists(),
            "has_models": (backend / "models").exists(),
            "has_workforce": (backend / "workforce").exists(),
            "has_agents": (backend / "agents").exists(),
            "has_audit": (backend / "audit").exists(),
            "has_cognition": (backend / "cognition").exists(),
        },
        "frontend": {
            "detected": frontend.exists(),
            "ts_files": _count_files(frontend, "**/*.ts") + _count_files(frontend, "**/*.tsx"),
            "has_pages": (frontend / "src" / "pages").exists(),
            "has_api_client": _exists(frontend, "src/lib/api.ts"),
        },
        "scripts": {
            "detected": scripts.exists(),
            "files": [f.name for f in scripts.iterdir()] if scripts.exists() else [],
        },
        "tests": {
            "detected": tests_root.exists(),
            "test_files": _count_files(tests_root),
            "backend_tests": _count_files(repo_root / "backend" / "tests"),
        },
        "docs": {
            "detected": docs.exists(),
            "has_audit_reports": (docs / "audit_reports").exists(),
            "files": [f.name for f in docs.iterdir() if f.is_file()] if docs.exists() else [],
        },
        "ci_cd": {
            "detected": (github / "workflows").exists(),
            "workflow_files": [f.name for f in (github / "workflows").iterdir()]
            if (github / "workflows").exists()
            else [],
        },
        "context_graph": {
            "module": _exists(backend, "context_graph"),
            "store": _exists(backend, "context_graph/store.py"),
        },
        "trust_graph": {
            "module": _exists(backend, "runtime/trust_graph.py"),
            "policy": _exists(backend, "governance/trust_policy.py"),
            "permissions": _exists(backend, "governance/agent_permissions.py"),
        },
        "orchestration": {
            "runtime_orchestrator": _exists(backend, "runtime/orchestrator.py"),
            "workforce_orchestrator": _exists(backend, "workforce/orchestrator.py"),
            "state_propagation": _exists(backend, "runtime/state_propagation.py"),
            "retry_guard": _exists(backend, "runtime/retry_guard.py"),
        },
        "memory_store": {
            "local": _exists(backend, "memory/local_second_brain.py"),
            "topology": _exists(backend, "memory/topology.py"),
            "manager": _exists(backend, "memory/memory_manager.py"),
            "winner_dna": _exists(backend, "memory/winner_dna.py"),
        },
        "governance": {
            "operating_law": _exists(backend, "governance/operating_law.py"),
            "decision_log": _exists(backend, "governance/decision_log.py"),
            "agent_permissions": _exists(backend, "governance/agent_permissions.py"),
        },
        "observability": {
            "has_health_endpoint": True,  # /api/v1/health in main.py
            "has_verification": _exists(backend, "runtime/verification.py"),
        },
        "replay": {
            "replay_runtime": _exists(backend, "runtime/replay.py"),
        },
        "audit": {
            "context_graph_audit": _exists(backend, "audit/context_graph_audit.py"),
            "trust_graph_audit": _exists(backend, "audit/trust_graph_audit.py"),
            "memory_audit": _exists(backend, "audit/memory_audit.py"),
            "artifact_audit": _exists(backend, "audit/artifact_audit.py"),
            "workforce_audit": _exists(backend, "audit/workforce_audit.py"),
            "replay_audit": _exists(backend, "audit/replay_audit.py"),
            "org_memory_audit": _exists(backend, "audit/org_memory_audit.py"),
            "economic_audit": _exists(backend, "audit/economic_audit.py"),
            "audit_orchestrator": _exists(backend, "audit/orchestrator.py"),
            "api_routes": _exists(backend, "api/v1/audit.py"),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Audit inventory scanner")
    parser.add_argument("--repo-root", default=".", help="Path to repository root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    print(f"Scanning repo: {repo_root}")

    topology = detect_topology(repo_root)
    inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "topology": topology,
    }

    out_dir = repo_root / "docs" / "audit_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "inventory.json"
    out_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Inventory written to: {out_path}")
    return inventory


if __name__ == "__main__":
    main()
