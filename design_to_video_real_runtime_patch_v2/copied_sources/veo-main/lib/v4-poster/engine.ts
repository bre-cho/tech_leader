import { buildPrompt } from "@/lib/v4-poster/prompt-compiler";
import { detectMechanism } from "@/lib/v4-poster/mechanism";
import { scoreVariant } from "@/lib/v4-poster/scoring";
import type { PosterInput, PosterResponse, VariantName, VisualVariant } from "@/lib/v4-poster/types";

const VARIANTS: VariantName[] = ["trust", "viral", "conversion"];

export function runAutoPosterV4(input: PosterInput): PosterResponse {
  const normalized: PosterInput = {
    ...input,
    goal: input.goal || "sale",
    ingredients: input.ingredients || [],
    hasModel: input.hasModel || false,
    hasPackaging: input.hasPackaging !== false,
    hasCollection: input.hasCollection || false,
    useReferenceImage: input.useReferenceImage || false
  };

  const mechanism = detectMechanism(normalized);
  const variants: VisualVariant[] = VARIANTS.map((variant) => {
    const compiled = buildPrompt(normalized, mechanism, variant);
    return {
      variant,
      label: compiled.label,
      sellingMechanism: mechanism,
      layout: compiled.layout,
      visualDirection: compiled.visualDirection,
      headlineStyle: compiled.headlineStyle,
      prompt: compiled.prompt,
      negativePrompt: compiled.negativePrompt,
      scores: scoreVariant(variant, compiled.prompt, normalized)
    };
  });

  const winner = [...variants].sort((a, b) => b.scores.finalScore - a.scores.finalScore)[0];

  return {
    input: normalized,
    mechanism,
    variants,
    winner,
    render: {
      mode: "provider_ready",
      status: "ready_for_provider",
      message: "Render contract compiled. Pass winner.prompt to a render provider (Adobe Firefly, Canva, etc.) to generate the image."
    }
  };
}
