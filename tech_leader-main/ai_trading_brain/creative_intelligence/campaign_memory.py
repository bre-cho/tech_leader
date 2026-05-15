from __future__ import annotations
from .models import CreativeAsset, CreativeScore, CampaignMemoryItem

class CampaignMemory:
    def update(self, asset: CreativeAsset, score: CreativeScore) -> CampaignMemoryItem:
        winner = [asset.hook, asset.offer] if score.total >= 85 else []
        loser = [] if score.total >= 70 else [asset.hook]
        return CampaignMemoryItem(
            campaign_id=f"campaign_{asset.platform}_{asset.asset_id}",
            winning_angles=winner,
            losing_angles=loser,
            reusable_dna={"visual_style": asset.visual_style, "audience": asset.audience, "score": score.total},
        )
