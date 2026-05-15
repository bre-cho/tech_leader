import type { PosterInput, VariantName, VariantScores } from "@/lib/v4-poster/types";

function clamp(value: number, min = 0, max = 100): number {
  return Math.max(min, Math.min(max, value));
}

export function scoreVariant(variant: VariantName, prompt: string, input: PosterInput): VariantScores {
  const text = `${variant} ${prompt} ${JSON.stringify(input)}`.toLowerCase();
  let ctr = 50;
  let attention = 50;
  let trust = 50;

  if (["price", "sale", "deal", "combo", "cta", "discount"].some((k) => text.includes(k))) ctr += 18;
  if (variant === "conversion") ctr += 12;
  if (["benefit", "clear", "retail-ready", "product dominance"].some((k) => text.includes(k))) ctr += 8;

  if (["explosion", "splash", "burst", "motion", "oversized", "impact"].some((k) => text.includes(k))) attention += 22;
  if (variant === "viral") attention += 15;
  if (["bold", "dramatic", "high contrast", "scroll-stopping"].some((k) => text.includes(k))) attention += 8;

  if (["feature", "proof", "ingredient", "icon", "scientific", "trust", "shield"].some((k) => text.includes(k))) trust += 20;
  if (variant === "trust") trust += 15;
  if (["readability", "no clutter", "clean", "specification"].some((k) => text.includes(k))) trust += 8;

  if (["clutter", "too many", "messy"].some((k) => text.includes(k))) {
    ctr -= 5;
    attention -= 5;
    trust -= 8;
  }

  ctr = clamp(ctr);
  attention = clamp(attention);
  trust = clamp(trust);

  return {
    ctr,
    attention,
    trust,
    finalScore: Math.round(ctr * 0.4 + attention * 0.35 + trust * 0.25)
  };
}
