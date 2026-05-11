from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


_HISTORY: list[dict[str, Any]] = []


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ReviewVariantEngine:
    """Minimal review-variant generator with in-memory history fallback."""

    def generate_variants(
        self,
        product_profile: dict[str, Any],
        *,
        count: int = 5,
        platform: str | None = None,
    ) -> list[dict[str, Any]]:
        safe_count = max(1, int(count or 1))
        product_name = str(product_profile.get("product_name") or "product").strip() or "product"
        audience = str(product_profile.get("target_audience") or "audience").strip() or "audience"
        platform_name = str(platform or product_profile.get("platform") or "shorts").strip().lower()

        variants: list[dict[str, Any]] = []
        for idx in range(safe_count):
            score = round(max(0.0, min(1.0, 0.55 + idx * 0.05)), 3)
            variants.append(
                {
                    "variant_id": f"variant-{idx + 1}",
                    "title_angle": f"{product_name} for {audience} ({idx + 1})",
                    "hook": f"Why {product_name} matters for {audience}",
                    "platform": platform_name,
                    "conversion_score": score,
                }
            )
        return variants

    def select_winner(self, variants: list[dict[str, Any]]) -> dict[str, Any]:
        if not variants:
            return {}
        return max(variants, key=lambda item: float(item.get("conversion_score", 0.0) or 0.0))

    def generate_variants_with_history(
        self,
        product_profile: dict[str, Any],
        *,
        count: int = 5,
        platform: str | None = None,
        context: dict[str, Any] | None = None,
        db: Any = None,  # noqa: ARG002
    ) -> dict[str, Any]:
        variants = self.generate_variants(product_profile, count=count, platform=platform)
        winner = self.select_winner(variants)
        run_id = str(uuid4())

        _HISTORY.append(
            {
                "run_id": run_id,
                "created_at": _now_iso(),
                "product_name": product_profile.get("product_name"),
                "platform": str(platform or product_profile.get("platform") or "").strip().lower() or None,
                "context": context or {},
                "variants": variants,
                "winner": winner,
            }
        )
        return {"run_id": run_id, "variants": variants, "winner": winner}

    @staticmethod
    def get_history(
        *,
        product_name: str | None = None,
        platform: str | None = None,
        limit: int = 20,
        db: Any = None,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        platform_key = str(platform or "").strip().lower()
        filtered = []
        for item in reversed(_HISTORY):
            if product_name and str(item.get("product_name") or "") != str(product_name):
                continue
            if platform_key and str(item.get("platform") or "") != platform_key:
                continue
            filtered.append(item)
            if len(filtered) >= max(1, int(limit or 1)):
                break
        return filtered
