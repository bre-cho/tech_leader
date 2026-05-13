import json
from sqlalchemy.orm import Session
from app.compound_os_mvp.db import CreativeVariant, MetricEvent, WinnerDNA

class CompoundOptimizationEngine:
    def select_winner(self, variants):
        return max(variants, key=lambda v: v.score)

    def ingest_metrics_and_update_scores(self, db: Session, event: MetricEvent):
        ctr = event.clicks / event.impressions if event.impressions else 0
        cvr = event.conversions / event.clicks if event.clicks else 0
        rpi = event.revenue / event.impressions if event.impressions else 0
        variant = db.query(CreativeVariant).filter(CreativeVariant.id == event.variant_id).first()
        if variant:
            performance_score = min(100, (ctr * 1000) + (cvr * 300) + (rpi * 10) + (event.watch_time_rate * 20))
            variant.score = round((variant.score * 0.6) + (performance_score * 0.4), 2)
            db.commit()
            db.refresh(variant)
        return {"ctr": ctr, "cvr": cvr, "revenue_per_impression": rpi, "updated_variant_score": variant.score if variant else None}

    def save_winner_dna(self, db: Session, brand_id: int, campaign_id: int, winner: CreativeVariant):
        storyboard = json.loads(winner.storyboard_json or "[]")
        dna = {
            "campaign_id": campaign_id,
            "variant_id": winner.id,
            "layout": winner.layout,
            "hook": winner.hook,
            "typography": winner.typography,
            "visual_style": winner.visual_style,
            "offer": winner.offer,
            "conversion_pattern": "attention → product desire → trust proof → CTA",
            "storyboard_pattern": " → ".join([s["purpose"] for s in storyboard]),
            "score": winner.score,
        }
        row = WinnerDNA(
            brand_id=brand_id,
            campaign_id=campaign_id,
            variant_id=winner.id,
            dna_json=json.dumps(dna, ensure_ascii=False),
            score=winner.score,
        )
        db.add(row)
        db.commit()
        return dna
