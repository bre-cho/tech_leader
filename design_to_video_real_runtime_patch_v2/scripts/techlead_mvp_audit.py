#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import shutil
import os
from pathlib import Path

ROOT = Path.cwd()
REPORT = {"checks": [], "go_no_go": "GO"}


def run_check(name: str, cmd: list[str]) -> None:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=120)
        ok = proc.returncode == 0
        REPORT["checks"].append({"name": name, "ok": ok, "stdout": proc.stdout[-3000:], "stderr": proc.stderr[-3000:]})
        if not ok:
            REPORT["go_no_go"] = "NO-GO"
    except Exception as exc:
        REPORT["checks"].append({"name": name, "ok": False, "error": str(exc)})
        REPORT["go_no_go"] = "NO-GO"


def exists_check(path: str) -> None:
    ok = (ROOT / path).exists()
    REPORT["checks"].append({"name": f"exists:{path}", "ok": ok})
    if not ok:
        REPORT["go_no_go"] = "NO-GO"


def api_contract_check() -> None:
    required_files = [
        "backend/app/api/v1/design.py",
        "backend/app/api/v1/upsell.py",
        "backend/app/api/v1/video.py",
        "backend/app/api/v1/offers.py",
        "backend/app/api/v1/crm.py",
        "backend/app/api/v1/memory.py",
        "backend/app/api/v1/dashboard.py",
        "backend/app/api/v1/render.py",
    ]
    missing = [p for p in required_files if not (ROOT / p).exists()]
    ok = len(missing) == 0
    REPORT["checks"].append({"name": "api_contract_files", "ok": ok, "missing": missing})
    if not ok:
        REPORT["go_no_go"] = "NO-GO"


def text_check(name: str, path: str, must_contain: list[str] | None = None, must_not_contain: list[str] | None = None) -> None:
    fp = ROOT / path
    if not fp.exists():
        REPORT["checks"].append({"name": name, "ok": False, "error": f"missing file: {path}"})
        REPORT["go_no_go"] = "NO-GO"
        return
    content = fp.read_text(encoding="utf-8")
    ok = True
    missing: list[str] = []
    present_blocked: list[str] = []
    for token in must_contain or []:
        if token not in content:
            ok = False
            missing.append(token)
    for token in must_not_contain or []:
        if token in content:
            ok = False
            present_blocked.append(token)
    REPORT["checks"].append({
        "name": name,
        "ok": ok,
        "missing": missing,
        "present_blocked": present_blocked,
    })
    if not ok:
        REPORT["go_no_go"] = "NO-GO"


def production_provider_config_check() -> None:
    app_env = os.getenv("APP_ENV", "development").lower()
    required_in_production = [
        "VIDEO_PROVIDER_ALLOW_MOCK",
        "IMAGE_GENERATION_REQUIRED",
        "VIDEO_RENDER_MODE",
    ]
    if app_env != "production":
        REPORT["checks"].append({"name": "provider_env_production", "ok": True, "skipped": "APP_ENV is not production"})
        return

    missing = [k for k in required_in_production if not os.getenv(k)]
    invalid = []
    if os.getenv("VIDEO_PROVIDER_ALLOW_MOCK", "").lower() != "false":
        invalid.append("VIDEO_PROVIDER_ALLOW_MOCK must be false")
    if os.getenv("IMAGE_GENERATION_REQUIRED", "").lower() != "true":
        invalid.append("IMAGE_GENERATION_REQUIRED must be true")
    if os.getenv("VIDEO_RENDER_MODE", "") != "real_provider":
        invalid.append("VIDEO_RENDER_MODE must be real_provider")

    ok = len(missing) == 0 and len(invalid) == 0
    REPORT["checks"].append({"name": "provider_env_production", "ok": ok, "missing": missing, "invalid": invalid})
    if not ok:
        REPORT["go_no_go"] = "NO-GO"


def runtime_gate_checks() -> None:
    text_check(
        "real_image_bridge_present",
        "backend/app/services/real_image_provider_bridge.py",
        must_contain=["class RealImageProviderBridge", "asset_url", "IMAGE_PROVIDER_MODE"],
    )
    text_check(
        "real_video_bridge_present",
        "backend/app/services/real_video_render_bridge.py",
        must_contain=["class RealVideoRenderBridge", "poll_policy", "retry_policy", "recovery_policy", "artifact_lineage"],
        must_not_contain=["dry_run"],
    )
    text_check(
        "render_endpoint_not_dry_run",
        "backend/app/api/v1/render.py",
        must_contain=["create_render_project", "RealVideoRenderBridge"],
        must_not_contain=["dry_run"],
    )
    text_check(
        "frontend_no_placeholder",
        "frontend/components/design-studio/ImageGallery.tsx",
        must_contain=["asset_url", "provider"],
        must_not_contain=["Image Placeholder"],
    )
    text_check(
        "artifact_lineage_model",
        "backend/app/models/design_to_video.py",
        must_contain=["class ArtifactLineage", "class WorkflowEvent"],
    )


def write_patch_report() -> None:
    report_md = ROOT / "docs" / "PATCH_REPORT.md"
    lines = [
        "# PATCH REPORT",
        "",
        f"- GO/NO-GO: {REPORT['go_no_go']}",
        "- Checks:",
    ]
    for check in REPORT["checks"]:
        status = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- [{status}] {check.get('name')}")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    exists_check("backend")
    exists_check("frontend")
    exists_check("docs")
    if (ROOT / "backend").exists():
        run_check("python_compile_backend", ["python", "-m", "compileall", "backend"])
    if (ROOT / "alembic").exists() or (ROOT / "backend/alembic").exists():
        if shutil.which("alembic"):
            run_check("alembic_heads", ["alembic", "heads"])
        else:
            REPORT["checks"].append({"name": "alembic_heads", "ok": True, "skipped": "alembic CLI not installed"})
    if (ROOT / "package.json").exists():
        run_check("npm_build", ["npm", "run", "build"])
    if (ROOT / "pytest.ini").exists() or (ROOT / "tests").exists():
        run_check("pytest", ["pytest", "-q"])
    api_contract_check()
    runtime_gate_checks()
    production_provider_config_check()
    out = ROOT / "docs" / "TECHLEAD_AUDIT_REPORT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")
    write_patch_report()
    print(json.dumps(REPORT, ensure_ascii=False, indent=2))
    raise SystemExit(0 if REPORT["go_no_go"] == "GO" else 1)
