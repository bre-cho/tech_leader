from app.ads_engine.schemas.contracts import WinnerScore

class WinnerSystem:
    def score(self, events):
        results = []
        for e in events:
            ctr = e.clicks / e.impressions if e.impressions else 0
            lead_rate = e.leads / e.clicks if e.clicks else 0
            sale_rate = e.sales / e.leads if e.leads else 0
            roas = e.revenue / e.spend if e.spend else 0
            score = min(ctr*1000,35) + min(lead_rate*100,25) + min(sale_rate*100,20) + min(roas*5,20)
            if score >= 85 and roas >= 1:
                decision, reason = "scale", "High winner score and positive ROAS."
            elif score >= 55:
                decision, reason = "iterate", "Potential winner, improve hook/visual/CTA."
            else:
                decision, reason = "kill", "Low signal; stop or rebuild creative."
            results.append(WinnerScore(variant_id=e.variant_id, ctr=round(ctr,4), lead_rate=round(lead_rate,4), sale_rate=round(sale_rate,4), roas=round(roas,2), winner_score=round(score,2), decision=decision, reason=reason))
        return sorted(results, key=lambda x: x.winner_score, reverse=True)
