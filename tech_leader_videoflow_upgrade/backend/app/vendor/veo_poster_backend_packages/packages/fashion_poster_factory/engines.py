from __future__ import annotations

import json
from pathlib import Path


class AutoCollageCompositionEngine:
    def compose(self, style: str) -> list[dict]:
        if style in ["luxury", "vogue"]:
            return [
                {"id": "hero", "type": "hero_image", "x": 0.25, "y": 0.18, "w": 0.56, "h": 0.64, "z": 10, "rotation": 0, "notes": "Clean hero, strong negative space."},
                {"id": "h1", "type": "headline", "x": 0.05, "y": 0.05, "w": 0.50, "h": 0.20, "z": 18, "rotation": 0, "notes": "Large refined serif, spacious tracking."},
                {"id": "photo_1", "type": "secondary_image", "x": 0.66, "y": 0.08, "w": 0.25, "h": 0.23, "z": 12, "rotation": 2, "notes": "Minimal framed image."},
                {"id": "quote", "type": "editorial_quote", "x": 0.07, "y": 0.36, "w": 0.28, "h": 0.17, "z": 20, "rotation": 0, "notes": "Elegant editorial quote; low noise."},
                {"id": "issue", "type": "issue_label", "x": 0.08, "y": 0.88, "w": 0.30, "h": 0.06, "z": 20, "rotation": 0, "notes": "Small issue/date label."},
            ]
        if style in ["y2k", "viral"]:
            return [
                {"id": "hero", "type": "hero_image", "x": 0.16, "y": 0.25, "w": 0.68, "h": 0.44, "z": 10, "rotation": -2, "notes": "Neon frame around hero."},
                {"id": "h1", "type": "headline", "x": 0.08, "y": 0.04, "w": 0.52, "h": 0.10, "z": 25, "rotation": 0, "notes": "Sticker-like headline."},
                {"id": "photo_1", "type": "secondary_image", "x": 0.03, "y": 0.14, "w": 0.35, "h": 0.22, "z": 13, "rotation": -5, "notes": "Polaroid with tape."},
                {"id": "photo_2", "type": "secondary_image", "x": 0.66, "y": 0.10, "w": 0.30, "h": 0.24, "z": 13, "rotation": 4, "notes": "Standing/candid image."},
                {"id": "sticker_1", "type": "sticker", "x": 0.05, "y": 0.47, "w": 0.18, "h": 0.10, "z": 30, "rotation": -8, "notes": "Heart/star/warning sign."},
                {"id": "ticket", "type": "ticket", "x": 0.58, "y": 0.72, "w": 0.35, "h": 0.15, "z": 28, "rotation": -4, "notes": "Y2K access ticket + barcode."},
            ]
        return [
            {"id": "hero", "type": "hero_image", "x": 0.18, "y": 0.22, "w": 0.62, "h": 0.56, "z": 10, "rotation": 0, "notes": "Hero model dominates center; keep face clear."},
            {"id": "h1", "type": "headline", "x": 0.04, "y": 0.04, "w": 0.58, "h": 0.16, "z": 20, "rotation": 0, "notes": "Large serif H1, can partially tuck behind hair/shoulder."},
            {"id": "photo_1", "type": "secondary_image", "x": 0.66, "y": 0.08, "w": 0.28, "h": 0.22, "z": 12, "rotation": -3, "notes": "Polaroid, full body/candid."},
            {"id": "photo_2", "type": "secondary_image", "x": 0.06, "y": 0.70, "w": 0.30, "h": 0.20, "z": 12, "rotation": 4, "notes": "Black-white or close-up."},
            {"id": "quote", "type": "editorial_quote", "x": 0.45, "y": 0.78, "w": 0.42, "h": 0.10, "z": 21, "rotation": -2, "notes": "Ripped paper quote card."},
            {"id": "barcode", "type": "barcode", "x": 0.04, "y": 0.91, "w": 0.24, "h": 0.05, "z": 22, "rotation": 0, "notes": "Magazine realism detail."},
        ]


class TypographyHierarchyEngine:
    def build(self, style: str, headline: str | None, subtitle: str | None, language: str) -> dict:
        defaults = {
            "dark_feminine": "HOTNESS",
            "luxury": "MODERN MUSE",
            "y2k": "GORGEOUS",
            "vogue": "MODEL",
            "viral": "MAIN CHARACTER",
        }
        h1 = headline or defaults.get(style, "HOTNESS")
        if subtitle:
            h2 = subtitle
        elif style == "dark_feminine":
            h2 = "Sac dep quyen luc" if language == "vi" else "Power Beauty"
        elif style == "luxury":
            h2 = "Nang tho hien dai" if language == "vi" else "Modern Muse"
        elif style == "y2k":
            h2 = "Dep me ly" if language == "vi" else "Drama Queen"
        elif style == "viral":
            h2 = "Ngot ngao nhung ca tinh" if language == "vi" else "Pretty but dangerous"
        else:
            h2 = "Bieu tuong thoi trang" if language == "vi" else "Fashion Icon"

        return {
            "h1": h1,
            "h2": h2,
            "h3": [
                "Khong can noi bat, vi em chinh la diem nhan." if language == "vi" else "Every day is a new opportunity to shine.",
                "Thanh lich - Ca tinh - Tinh te" if language == "vi" else "Elegant - Bold - Iconic",
                "Ve dep khien ban khong the roi mat" if language == "vi" else "A beauty you cannot ignore",
            ],
            "h4": ["Vietnam Edition", "Limited Editorial", "2026 Collection", "Issue 01"],
            "font_logic": {
                "h1": "Didot/Bodoni style serif" if style in ["luxury", "vogue", "dark_feminine"] else "bold condensed sans / playful serif mix",
                "h2": "Elegant serif italic" if style in ["luxury", "vogue", "dark_feminine"] else "rounded sans",
                "body": "clean sans-serif" if style in ["luxury", "vogue", "dark_feminine"] else "compact sans",
            },
            "hierarchy_notes": [
                "H1 takes 18-28% poster area.",
                "H2 should stay near H1 to lock mood.",
                "H3/H4 are texture info only.",
                "Do not cover eyes, lips, shoulders or hero product.",
            ],
        }


class LuxuryCampaignEngine:
    def route(self, style: str, palette: list[str] | None) -> dict:
        if style == "dark_feminine":
            return {
                "palette": palette or ["black", "deep red", "ivory white"],
                "lighting": "cinematic directional light, glossy highlights, deep contrast",
                "texture": ["subtle film grain", "scratched print texture", "ripped paper edges", "deep red brush accents"],
                "noise_level": "medium-controlled",
            }
        if style in ["y2k", "viral"]:
            return {
                "palette": palette or ["hot pink", "black", "white", "chrome"],
                "lighting": "flash photography, neon rim glow, high contrast",
                "texture": ["plastic sticker shine", "transparent tape", "polaroid paper", "barcode", "UI icons"],
                "noise_level": "high-controlled",
            }
        return {
            "palette": palette or ["ivory", "deep burgundy", "black", "soft gold"],
            "lighting": "premium soft cinematic light, clean shadow falloff",
            "texture": ["premium paper grain", "minimal torn edge", "subtle ink texture"],
            "noise_level": "low-premium",
        }

    def negative_prompt(self) -> str:
        return (
            "low quality, blurry, bad typography, unreadable text, extra fingers, distorted face, "
            "plastic skin, over-smoothed skin, cluttered composition, random stickers, watermark, logo artifacts"
        )


class FashionScoreEngine:
    def score(self, style: str, route: dict, layout: list[dict], typography: dict) -> dict:
        attention = 86
        luxury = 82
        editorial = 84
        readability = 83
        viral = 80
        brand_identity = 84

        if style in ["dark_feminine", "y2k", "viral"]:
            attention += 7
            viral += 8
        if style in ["luxury", "vogue", "dark_feminine"]:
            luxury += 8
            editorial += 8
        if len(layout) > 7:
            readability -= 6
        if route.get("noise_level") == "high-controlled":
            attention += 4
            readability -= 3
        if typography.get("h1"):
            brand_identity += 4
            attention += 2

        scores = {
            "attention": min(attention, 99),
            "luxury": min(luxury, 99),
            "editorial": min(editorial, 99),
            "readability": min(readability, 99),
            "viral": min(viral, 99),
            "brand_identity": min(brand_identity, 99),
        }
        scores["total"] = round(sum(scores.values()) / len(scores))
        return scores


class WinnerDNAMemory:
    def __init__(self, path: str = "data/winner_dna_fashion.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save_if_winner(self, dna: dict, score: dict, threshold: int = 88) -> bool:
        if score.get("total", 0) < threshold:
            return False

        records: list[dict] = []
        if self.path.exists():
            try:
                records = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                records = []

        signature = "|".join([
            str(dna.get("style")),
            str(dna.get("palette")),
            str(dna.get("hero_crop")),
            str(dna.get("layout")),
        ])

        if any(
            "|".join([
                str(r.get("style")),
                str(r.get("palette")),
                str(r.get("hero_crop")),
                str(r.get("layout")),
            ]) == signature
            for r in records
        ):
            return False

        records.append({**dna, "scores": score})
        self.path.write_text(json.dumps(records[-200:], ensure_ascii=False, indent=2), encoding="utf-8")
        return True
