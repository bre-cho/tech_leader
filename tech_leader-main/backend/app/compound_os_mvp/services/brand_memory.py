import json
from sqlalchemy.orm import Session
from app.compound_os_mvp.db import Brand

DEFAULT_MEMORY = {
    "brand_identity": {},
    "typography": [],
    "spacing": {},
    "visual_rhythm": [],
    "campaign_evolution": [],
    "tone": "",
    "positioning": "",
    "emotional_direction": [],
    "winning_layouts": [],
    "winning_hooks": [],
    "winning_typography": [],
    "luxury_signals": [],
    "conversion_patterns": [],
    "storyboard_patterns": [],
    "offer_structures": []
}

class BrandMemoryCloud:
    def get_or_create(self, db: Session, name: str, industry: str, identity=None):
        brand = db.query(Brand).filter(Brand.name == name).first()
        if brand:
            return brand
        memory = DEFAULT_MEMORY.copy()
        memory["brand_identity"] = identity or {}
        brand = Brand(name=name, industry=industry, identity_json=json.dumps(identity or {}), memory_json=json.dumps(memory))
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand

    def recall(self, brand: Brand):
        try:
            return json.loads(brand.memory_json or "{}")
        except Exception:
            return DEFAULT_MEMORY.copy()

    def update_from_winner(self, db: Session, brand: Brand, winner):
        memory = self.recall(brand)
        memory.setdefault("campaign_evolution", []).append({
            "campaign_id": winner.get("campaign_id"),
            "variant_id": winner.get("variant_id"),
            "score": winner.get("score"),
        })
        for key, source_key in [
            ("winning_layouts", "layout"),
            ("winning_hooks", "hook"),
            ("winning_typography", "typography"),
            ("conversion_patterns", "conversion_pattern"),
            ("storyboard_patterns", "storyboard_pattern"),
            ("offer_structures", "offer"),
        ]:
            value = winner.get(source_key)
            if value and value not in memory.setdefault(key, []):
                memory[key].append(value)
        brand.memory_json = json.dumps(memory, ensure_ascii=False)
        db.commit()
        return memory
