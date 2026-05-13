class BillboardPrintEngine:
    def reason(self, aspect_ratio: str, targets: list[str]) -> dict:
        is_print = any(t in {"poster","billboard","print","lightbox","magazine"} for t in targets)
        return {
            "export_targets": targets,
            "aspect_ratio": aspect_ratio,
            "print_ready": is_print,
            "min_requirements": {
                "web_preview":"1600px short edge",
                "social":"2160px vertical preferred",
                "print":"300 DPI export path; keep text vector/frontend-rendered when possible",
                "billboard":"large-format contrast and clean silhouette",
            },
            "qa": ["contrast safe", "text readable", "no edge artifacts", "upscale integrity", "CMYK review required before production print"],
        }
