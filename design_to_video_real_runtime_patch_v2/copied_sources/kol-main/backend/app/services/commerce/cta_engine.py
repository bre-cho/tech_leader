from __future__ import annotations


class CTAEngine:
    """Compatibility CTA engine used by avatar_commerce routes."""

    def generate(
        self,
        *,
        intent: str | None = None,
        product_name: str | None = None,
        target_audience: str | None = None,
        discount: str | None = None,
        deadline: str | None = None,
    ) -> str:
        action = {
            "buy_now": "Mua ngay",
            "learn_more": "Tìm hiểu thêm",
            "sign_up": "Đăng ký ngay",
        }.get((intent or "").strip().lower(), "Khám phá ngay")
        product = (product_name or "sản phẩm").strip()
        audience = (target_audience or "").strip()
        details = []
        if discount:
            details.append(str(discount).strip())
        if deadline:
            details.append(f"đến {str(deadline).strip()}")
        detail_text = f" ({', '.join(details)})" if details else ""
        if audience:
            return f"{action} {product} cho {audience}{detail_text}".strip()
        return f"{action} {product}{detail_text}".strip()

    def generate_all(
        self,
        *,
        intent: str | None = None,
        product_name: str | None = None,
        target_audience: str | None = None,
        discount: str | None = None,
        deadline: str | None = None,
    ) -> list[str]:
        primary = self.generate(
            intent=intent,
            product_name=product_name,
            target_audience=target_audience,
            discount=discount,
            deadline=deadline,
        )
        secondary = f"Tìm hiểu {product_name or 'sản phẩm'} ngay hôm nay".strip()
        tertiary = f"Đừng bỏ lỡ {product_name or 'ưu đãi này'}".strip()
        return [primary, secondary, tertiary]
