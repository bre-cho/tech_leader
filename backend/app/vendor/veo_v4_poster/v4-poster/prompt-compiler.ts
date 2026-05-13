import { selectLayout } from "@/lib/v4-poster/layout";
import type { MechanismResult, PosterInput, VariantName } from "@/lib/v4-poster/types";

const NEGATIVE_PROMPT =
  "low quality, blurry, cluttered, unreadable text, distorted logo, wrong packaging, extra limbs, bad anatomy, watermark, messy composition, product too small, lighting mismatch";

const VARIANT_COPY: Record<VariantName, { label: string; visual: string; headline: string; inject: string }> = {
  trust: {
    label: "Trust Version - Build belief",
    visual: "Clean premium layout, proof icons, ingredient or feature panels, readable benefit hierarchy.",
    headline: "Specific benefits with proof. Avoid exaggerated claims.",
    inject: "clean feature infographic, proof badges, readable icons, scientific clarity, trustworthy composition"
  },
  viral: {
    label: "Viral Version - Drive attention",
    visual: "Oversized product hero, splash/explosion/orbit, high contrast, short powerful hook.",
    headline: "Strong hook, minimal text, stop-scroll in 3 seconds.",
    inject: "oversized hero product, explosive splash, dynamic motion, ingredient burst, high contrast lighting"
  },
  conversion: {
    label: "Conversion Version - Drive action",
    visual: "Product clearest, benefit hierarchy, offer/price/CTA area, retail-ready design.",
    headline: "Direct reason to buy with key benefit and CTA.",
    inject: "clear CTA zone, price highlight, benefit hierarchy, product dominance, retail-ready layout"
  }
};

const MECHANISM_INJECT: Record<string, string> = {
  ingredient: "ingredients orbiting and merging into product, realistic texture, fusion transformation",
  offer: "promotion cluster, price badge, combo display, strong sale hierarchy",
  emotion: "cinematic storytelling world, emotional symbols, memory scene",
  energy: "splash explosion, impact burst, motion particles, dramatic shadow",
  feature: "technical feature callouts, proof icons, specification panels",
  lifestyle: "real-life usage scenes, lifestyle mini panels, aspirational environment",
  luxury: "premium dark background, macro detail, elegant reflection, gold highlights",
  lookbook: "editorial grid, multi-frame styling, magazine lookbook layout"
};

export function buildPrompt(
  input: PosterInput,
  mechanism: MechanismResult,
  variant: VariantName
): {
  label: string;
  visualDirection: string;
  headlineStyle: string;
  layout: string;
  prompt: string;
  negativePrompt: string;
} {
  const ingredients = (input.ingredients || []).length
    ? (input.ingredients || []).join(", ")
    : "relevant product elements";
  const layout = selectLayout(mechanism.primary, mechanism.secondary);
  const copy = VARIANT_COPY[variant];
  const primaryLogic = MECHANISM_INJECT[mechanism.primary] || "premium product advertising logic";
  const secondaryLogic = mechanism.secondary ? MECHANISM_INJECT[mechanism.secondary] || "" : "";
  const headline = input.headline || `Premium poster for ${input.productName}`;

  const prompt = [
    "ultra high-end commercial advertising poster",
    `product: ${input.productName}`,
    `industry: ${input.industry}, product type: ${input.productType || "premium product"}`,
    `main headline concept: ${headline}`,
    "hero product must dominate 60-70% of visual hierarchy",
    `layout: ${layout}`,
    `primary selling mechanism: ${mechanism.primary}`,
    `secondary selling mechanism: ${mechanism.secondary || "none"}`,
    `mechanism visual logic: ${primaryLogic}, ${secondaryLogic}`,
    `ingredients/elements: ${ingredients}`,
    `variant strategy: ${variant}, ${copy.inject}`,
    "clean premium composition, product sharp and recognizable",
    "text area less than 10% of composition, strong readability zones",
    "unified color palette, consistent lighting direction",
    "ultra realistic texture, depth of field, cinematic commercial photography",
    "advertising agency quality, high visual impact, no clutter"
  ].join(", ");

  return {
    label: copy.label,
    visualDirection: copy.visual,
    headlineStyle: copy.headline,
    layout,
    prompt,
    negativePrompt: NEGATIVE_PROMPT
  };
}
