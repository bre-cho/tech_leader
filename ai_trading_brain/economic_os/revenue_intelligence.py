from __future__ import annotations
from .models import EconomicInput

class RevenueIntelligence:
    def analyze(self, data: EconomicInput) -> dict:
        profit = data.revenue - data.ad_spend - data.product_cost
        roas = data.revenue / data.ad_spend if data.ad_spend else 0
        aov = data.revenue / data.customers if data.customers else 0
        return {"revenue": data.revenue, "profit": round(profit, 2), "roas": round(roas, 2), "average_order_value": round(aov, 2)}
