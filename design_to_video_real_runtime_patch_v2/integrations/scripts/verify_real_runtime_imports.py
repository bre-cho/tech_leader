from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

REQUIRED_MODULES = [
    "app.services.real_image_provider_bridge",
    "app.services.real_video_render_bridge",
    "app.providers.factory",
    "app.providers.veo.adapter",
    "app.providers.runway.adapter",
    "app.providers.kling.adapter",
    "app.providers.seedance.adapter",
    "app.providers.seedance2.adapter",
    "app.services.provider_router",
    "app.services.render_orchestrator",
]


def main() -> int:
    results = []
    for name in REQUIRED_MODULES:
        try:
            importlib.import_module(name)
            results.append({"module": name, "ok": True})
        except Exception as exc:
            results.append({"module": name, "ok": False, "error": str(exc)})
    Path("REAL_RUNTIME_IMPORT_REPORT.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    failed = [r for r in results if not r["ok"]]
    if failed:
        print(json.dumps(failed, indent=2))
        return 1
    print("real runtime import check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
