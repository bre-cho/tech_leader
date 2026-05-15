import type { BeautyCommerceInput, EngineReport } from "./types";

export function runProductAttentionRouting(input: BeautyCommerceInput): EngineReport {
  const hasProduct = Boolean(input.productName);
  return {
    name: "ProductAttentionRouting",
    score: hasProduct ? 96 : 84,
    data: hasProduct
      ? {
          product: input.productName,
          sequence: [
            { beat: "0-2s", action: "look at camera, establish trust" },
            { beat: "2-4s", action: "raise product into frame" },
            { beat: "4-6s", action: "eyes glance to product, rotate product slightly" },
            { beat: "6-9s", action: "show texture/benefit/demo cue" },
            { beat: "9-12s", action: "smile and return gaze to camera" },
            { beat: "final", action: "CTA with product visible" }
          ],
          productRules: [
            "label/shape must remain readable",
            "hand must not cover key product identity",
            "product movement must be smooth and plausible"
          ]
        }
      : {
          sequence: [
            { beat: "0-2s", action: "look at camera" },
            { beat: "2-5s", action: "show fashion/detail/lifestyle cue" },
            { beat: "final", action: "brand memory pose" }
          ],
          productRules: ["No product supplied; route attention to fashion/beauty outcome."]
        },
    warnings: hasProduct ? [] : ["No productName provided; product attention routing downgraded."]
  };
}
