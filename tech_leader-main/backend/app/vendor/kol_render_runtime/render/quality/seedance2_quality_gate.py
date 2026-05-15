from __future__ import annotations

from typing import Any


def evaluate_seedance2_quality(render_result: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    checks = []
    output_url = render_result.get("output_url") or render_result.get("url")
    checks.append({"name": "output_url_present", "pass": bool(output_url)})

    if "duration_sec" in expected and "duration_sec" in render_result:
        delta = abs(float(render_result["duration_sec"]) - float(expected["duration_sec"]))
        checks.append({"name": "duration_match", "pass": delta <= 0.5, "delta": delta})

    if expected.get("aspect_ratio") and render_result.get("aspect_ratio"):
        checks.append({
            "name": "aspect_ratio_match",
            "pass": expected["aspect_ratio"] == render_result["aspect_ratio"],
        })

    if expected.get("reference_required"):
        checks.append({"name": "reference_fidelity_required", "pass": render_result.get("reference_score", 1.0) >= 0.75})

    passed = all(c.get("pass") for c in checks)
    return {"provider": "seedance2", "passed": passed, "checks": checks}
