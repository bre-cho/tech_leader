import type { BeautyCommerceRequest } from "./beautyCommerceTypes";

export function buildBeautyAttentionRouting(req: BeautyCommerceRequest) {
  const product = Boolean(req.productName);
  const route = product
    ? ["eyes/face", "neckline-or-silhouette", "product-in-hand", "benefit-proof", "CTA"]
    : ["eyes/face", "silhouette", "fashion-detail", "brand-emotion", "CTA"];

  if (req.channel === "tiktok") {
    route.unshift("first-frame-hook");
  }

  return {
    route,
    firstGlanceAnchor: "face and eye contact",
    dopaminePoints: ["soft smile", "skin glow", "fabric detail", "pose confidence"],
    retentionPoints: ["gaze direction", "micro expression", "hand gesture", "product/pose transition"],
    conversionPoints: product ? ["product visibility", "benefit proof", "clear CTA"] : ["brand desire", "lookbook aspiration", "save/share intent"],
    rule: "Do not make styling explicit; keep it tasteful, fashion-commercial and brand-safe."
  };
}
