import type { IndustryDetectResult } from "./types";

export class AutoIndustryDetector {
  detect(input: { text: string; product_name?: string; image_description?: string; metadata?: Record<string, unknown> }): IndustryDetectResult {
    const text = input.text.toLowerCase();
    const industry = text.includes("beauty") ? "beauty" : text.includes("fashion") ? "fashion" : "general";
    return { industry, confidence: 0.82, reasons: ["keyword match", "fallback heuristic"] };
  }
}
