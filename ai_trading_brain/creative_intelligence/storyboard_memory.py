from __future__ import annotations
from .models import CreativeAsset, StoryboardMemoryItem

class StoryboardMemory:
    def generate_seed_scenes(self, asset: CreativeAsset) -> list[StoryboardMemoryItem]:
        return [
            StoryboardMemoryItem("scene_01_hook", f"Mở đầu mạnh: {asset.hook}, phong cách {asset.visual_style}", "close-up / push-in", "hook", "Giữ cùng màu sắc và nhân vật chính."),
            StoryboardMemoryItem("scene_02_problem", f"Thể hiện nỗi đau của nhóm {asset.audience}", "medium shot / handheld subtle", "problem", "Không đổi tông ánh sáng."),
            StoryboardMemoryItem("scene_03_solution", f"Giới thiệu lời hứa: {asset.offer}", "hero shot / slow dolly", "solution", "Giữ logo/visual motif nhất quán."),
            StoryboardMemoryItem("scene_04_cta", "Kêu gọi hành động rõ, ít chữ, dễ nhớ", "front-facing clean frame", "conversion", "Kết thúc bằng visual key."),
        ]
