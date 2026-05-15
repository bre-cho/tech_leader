import type { BananaRequest } from "./bananaTypes";

export function buildConsistencyMemory(req: BananaRequest) {
  const referenceLabels = req.images.map((img, idx) => img.label ?? `reference_${idx + 1}`);
  return {
    hasReferences: req.images.length > 0,
    referenceCount: req.images.length,
    referenceLabels,
    consistencyRules: [
      "preserve product shape and logo when provided",
      "preserve avatar/character identity when provided",
      "preserve layout/template if input is a template",
      "do not change text meaning unless specifically asked",
      "maintain brand color and material cues"
    ],
    promptInjection: referenceLabels.length
      ? `Use these references as locked identity/object anchors: ${referenceLabels.join(", ")}.`
      : "No external references provided."
  };
}
