from app.creative_os_mvp.models.schemas import CreativeRequest

class AttentionRoutingEngine:
    """Computes the intended visual scan path and attention weights."""
    def reason(self, req: CreativeRequest) -> dict:
        industry = req.brand.industry.lower()
        if industry in {"beauty", "cosmetics", "wellness"}:
            route = [
                ("face/skin glow", 0.92, "emotional anchor and trust"),
                ("product foreground", 0.88, "desire trigger"),
                ("headline", 0.78, "promise framing"),
                ("benefit cue", 0.68, "reason to believe"),
                ("CTA", 0.74, "conversion endpoint"),
            ]
        elif industry in {"fmcg", "sports grooming"}:
            route = [
                ("oversized headline", 0.9, "billboard hook"),
                ("cooling motion/effect", 0.84, "dopamine and sensory proof"),
                ("product hero", 0.89, "pack recognition"),
                ("human reaction", 0.72, "usage context"),
                ("CTA/offer", 0.76, "action"),
            ]
        else:
            route = [
                ("hero subject", .86, "primary anchor"),
                ("product/offer", .82, "value"),
                ("headline", .80, "message"),
                ("CTA", .72, "action"),
            ]
        return {
            "scan_path": [
                {"rank": i+1, "element": e, "weight": w, "reason": r}
                for i,(e,w,r) in enumerate(route)
            ],
            "dopamine_triggers": ["motion cue", "contrast", "beauty/texture detail", "sensory particles"],
            "attention_risk": "blocked" if len(route) < 3 else "controlled",
        }
