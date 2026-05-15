from __future__ import annotations
import argparse, json

from _repo_bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from ai_trading_brain.architecture_observer import ArchitectureObserverRuntime

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--changed", nargs="*", default=[])
    args = parser.parse_args()
    report = ArchitectureObserverRuntime(args.repo).run(args.changed)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
