from __future__ import annotations
from .models import EconomicInput

class TrafficIntelligence:
    def analyze(self, data: EconomicInput) -> dict:
        lead_rate = data.leads / data.traffic if data.traffic else 0
        customer_rate = data.customers / data.traffic if data.traffic else 0
        cpc_proxy = data.ad_spend / data.traffic if data.traffic else 0
        return {"traffic": data.traffic, "lead_rate": round(lead_rate, 4), "customer_rate": round(customer_rate, 4), "cost_per_visit_proxy": round(cpc_proxy, 4)}
