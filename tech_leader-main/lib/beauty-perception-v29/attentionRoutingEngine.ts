import type { BeautyPerceptionRequest, EngineResult } from "./types";

export function runBeautyAttentionRoutingEngine(req: BeautyPerceptionRequest): EngineResult {
  const product = Boolean(req.productName);
  const route = product
    ? ["eyes", "smile", "product", "lips/skin glow", "collarbone/fashion frame", "CTA"]
    : ["eyes", "lips", "collarbone", "dress silhouette", "hair highlights", "background mood"];

  const heatmap = route.map((target, index) => ({
    target,
    order: index + 1,
    attention_weight: Number((1 - index * 0.1).toFixed(2)),
    purpose:
      target === "eyes" ? "trust and attention lock" :
      target === "product" ? "commercial conversion" :
      target.includes("collarbone") ? "elegance and attention routing" :
      target.includes("hair") ? "luxury texture and face framing" :
      "supporting beauty perception"
  }));

  return {
    name: "BeautyAttentionRoutingEngine",
    score: 96,
    data: {
      route,
      heatmap,
      core_rule: "Beauty is treated as an attention routing system, not a static pretty face."
    },
    warnings: []
  };
}
