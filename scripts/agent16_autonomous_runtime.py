from __future__ import annotations
import json
from dataclasses import asdict

from _repo_bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from ai_trading_brain.autonomous_runtime import AutonomousRuntime

if __name__ == "__main__":
    report = AutonomousRuntime().run("upgrade agent16 into autonomous operating environment")
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
