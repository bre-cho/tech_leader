import type { BeautyCommerceInput, EngineReport } from "./types";

export function runTikTokBeautyCompositionEngine(input: BeautyCommerceInput): EngineReport {
  return {
    name: "TikTokBeautyCompositionEngine",
    score: input.channel === "tiktok" || input.channel === "livestream" ? 96 : 88,
    data: {
      frame: "vertical 9:16",
      firstFrame: [
        "face visible in first glance",
        "eyes readable",
        "product or beauty outcome visible if commercial",
        "leave lower subtitle safe zone",
        "avoid right-side UI conflict"
      ],
      layout: input.productName
        ? "face upper third, product mid-frame or hand-held near face, CTA/subtitle lower safe zone"
        : "face and upper body centered with fashion/lifestyle negative space",
      retention: ["micro-expression within 0.7s", "gesture within 1.5s", "product/value cue before 3s"]
    },
    warnings: input.channel !== "tiktok" ? ["Composition optimized for TikTok but channel is not TikTok."] : []
  };
}
