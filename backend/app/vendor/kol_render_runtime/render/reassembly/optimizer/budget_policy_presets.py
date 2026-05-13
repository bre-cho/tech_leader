from __future__ import annotations


_PRESETS: dict[str, dict[str, float | bool | str]] = {
    "cheap": {
        "policy": "cheap",
        "max_rebuild_cost": 2.0,
        "max_rebuild_time_sec": 90.0,
        "allow_budget_downgrade": True,
        "include_optional_rebuilds": False,
    },
    "balanced": {
        "policy": "balanced",
        "max_rebuild_cost": 5.0,
        "max_rebuild_time_sec": 180.0,
        "allow_budget_downgrade": True,
        "include_optional_rebuilds": False,
    },
    "quality": {
        "policy": "quality",
        "max_rebuild_cost": 20.0,
        "max_rebuild_time_sec": 600.0,
        "allow_budget_downgrade": True,
        "include_optional_rebuilds": True,
    },
    "emergency": {
        "policy": "emergency",
        "max_rebuild_cost": 1.0,
        "max_rebuild_time_sec": 60.0,
        "allow_budget_downgrade": False,
        "include_optional_rebuilds": False,
    },
}


def resolve_budget_policy(policy: str | None) -> dict[str, float | bool | str]:
    key = str(policy or "balanced").strip().lower()
    return dict(_PRESETS.get(key, _PRESETS["balanced"]))
