import type { BeautyCommerceRequest } from "./beautyCommerceTypes";

export function predictBeautyConversion(req: BeautyCommerceRequest, score: Record<string, any>) {
  const final = Number(score.final_score ?? 80);
  const channelBoost = req.channel === "tiktok" ? 4 : req.channel === "instagram" ? 3 : 0;
  const productBoost = req.productName ? 5 : 0;
  const predictedCtr = Math.min(6.5, Math.max(1.2, (final - 70) / 8 + channelBoost / 10 + productBoost / 10));

  return {
    predicted_ctr_percent: Number(predictedCtr.toFixed(2)),
    likely_conversion_driver: req.productName ? "face-product alignment + product trust" : "fashion aspiration + save/share appeal",
    optimization: [
      "increase first-frame face/product clarity",
      "keep CTA below trust proof",
      "use gaze direction to guide attention",
      "preserve natural skin and fabric realism"
    ],
    confidence: final >= 90 ? "high" : final >= 82 ? "medium" : "low"
  };
}
