import type { BananaRequest, BananaArtifact } from "./bananaTypes";

export function scoreBananaCommercial(req: BananaRequest, artifacts: BananaArtifact[]) {
  const prompt = req.prompt.toLowerCase();
  const scores = {
    commercial_relevance: hasAny(prompt, ["ad", "poster", "campaign", "product", "brand", "cta", "tiktok"]) ? 92 : 78,
    typography_readiness: hasAny(prompt, ["text", "headline", "typography", "billboard", "poster"]) ? 90 : 76,
    product_hero_strength: hasAny(prompt, ["product", "bottle", "serum", "perfume", "packshot", "hero"]) ? 93 : 75,
    consistency_readiness: req.images.length > 0 ? 94 : 72,
    artifact_integrity: artifacts.length > 0 && artifacts.every((a) => a.sizeBytes > 0) ? 100 : 0
  };
  const average = Object.values(scores).reduce((a, b) => a + b, 0) / Object.values(scores).length;

  return {
    ...scores,
    final_score: Math.round(average),
    pass: average >= 85,
    winner_dna_ready: average >= 90,
    notes: [
      "Use actual rendered image QA in production for OCR/logo/face/object validation.",
      "This scoring is runtime pre/post contract scoring and artifact integrity gate."
    ]
  };
}

function hasAny(text: string, words: string[]) {
  return words.some((w) => text.includes(w));
}
