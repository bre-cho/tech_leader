from __future__ import annotations
import json
from dataclasses import asdict

from _repo_bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from ai_trading_brain.creative_intelligence.models import CreativeAsset
from ai_trading_brain.creative_intelligence import CreativeIntelligenceRuntime

if __name__ == "__main__":
    asset = CreativeAsset("demo", "AI Native Business OS", "Build your AI workforce", "founders", "operating system template", "luxury tech editorial")
    report = CreativeIntelligenceRuntime().run(asset)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
