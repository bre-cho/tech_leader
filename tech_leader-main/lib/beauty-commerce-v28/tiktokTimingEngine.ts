import type { BeautyCommerceInput, EngineReport } from "./types";

export function runTikTokTimingEngine(input: BeautyCommerceInput): EngineReport {
  const duration = input.durationSec;
  return {
    name: "TikTokCommercialTiming",
    score: 95,
    data: {
      durationSec: duration,
      pacingMap: [
        { t: "0.0-1.0", purpose: "visual hook: eye contact + face clarity" },
        { t: "1.0-3.0", purpose: "problem/desire cue" },
        { t: "3.0-6.0", purpose: "product or fashion proof" },
        { t: "6.0-10.0", purpose: "benefit demo + trust cue" },
        { t: "10.0-final", purpose: "CTA + product/brand recall" }
      ],
      subtitleSafeZone: "lower third, above app UI",
      retentionRules: [
        "micro motion every 1.5-2s",
        "visual value before 3s",
        "product/benefit before midpoint",
        "CTA only after trust proof"
      ]
    },
    warnings: input.durationSec > 30 ? ["Long TikTok duration; consider stronger mid-video retention hook."] : []
  };
}
