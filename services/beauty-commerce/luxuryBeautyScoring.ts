import type { BeautyCommerceRequest } from "./beautyCommerceTypes";

export function scoreLuxuryBeautyInputs(req: BeautyCommerceRequest) {
  const text = `${req.brandName} ${req.industry} ${req.outfitStyle} ${req.avatarDescription}`.toLowerCase();
  const hasLuxury = /luxury|premium|editorial|high-end|cao cấp|sang trọng/.test(text);
  const hasBeauty = /beauty|skin|makeup|cosmetic|spa|fashion|kol/.test(text);
  const hasProduct = Boolean(req.productName || req.productType);
  const hasReferences = req.references.length > 0;

  const scores = {
    luxury_perception: hasLuxury ? 92 : 78,
    beauty_relevance: hasBeauty ? 94 : 80,
    product_commerce_readiness: hasProduct ? 91 : 76,
    consistency_readiness: hasReferences ? 92 : 74,
    channel_fit: req.channel === "tiktok" || req.channel === "instagram" ? 91 : 84
  };
  const final = Math.round(Object.values(scores).reduce((a, b) => a + b, 0) / Object.values(scores).length);

  return {
    ...scores,
    final_score: final,
    pass: final >= 82,
    recommendation: final >= 90 ? "winner_dna_candidate" : "preview_and_iterate"
  };
}
