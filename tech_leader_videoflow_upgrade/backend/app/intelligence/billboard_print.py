from __future__ import annotations


class BillboardPrintEngine:
    def plan(self, export_targets):
        targets = set(export_targets)
        return {
            "targets": list(targets),
            "print_rules": {
                "billboard_ready": "billboard" in targets,
                "min_export_resolution": "7680px long edge for 8K master",
                "contrast": "large-format safe",
                "cmyk_notes": "avoid neon-only detail, preserve skin tones before conversion",
                "safe_margins": "8% outer margin for print bleed and crop",
                "text_rendering": "prefer frontend/vector text overlay for final production",
            },
            "exports": [
                {"name": "social_4x5", "size": "2160x2700"},
                {"name": "tiktok_9x16", "size": "2160x3840"},
                {"name": "billboard_8k", "size": "7680x4320"},
                {"name": "print_a1", "size": "7016x9933"},
            ],
        }
