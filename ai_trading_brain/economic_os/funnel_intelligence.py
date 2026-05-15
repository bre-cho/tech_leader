from __future__ import annotations
from .models import EconomicInput

class FunnelIntelligence:
    def analyze(self, data: EconomicInput) -> dict:
        visit_to_lead = data.leads / data.traffic if data.traffic else 0
        lead_to_customer = data.customers / data.leads if data.leads else 0
        bottleneck = "traffic_to_lead" if visit_to_lead < lead_to_customer else "lead_to_customer"
        return {"visit_to_lead": round(visit_to_lead, 4), "lead_to_customer": round(lead_to_customer, 4), "primary_bottleneck": bottleneck}
