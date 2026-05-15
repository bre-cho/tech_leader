import type { Mechanism, MechanismResult, PosterInput } from "@/lib/v4-poster/types";

const KEYWORDS: Record<Mechanism, string[]> = {
  ingredient: ["matcha", "collagen", "honey", "milk", "tea", "ingredient", "organic", "natural"],
  offer: ["price", "combo", "sale", "discount", "buy 1", "promo", "deal"],
  energy: ["energy", "power", "strong", "sport", "gym", "performance", "challenge"],
  emotion: ["memory", "family", "happy", "festival", "love", "story"],
  feature: ["technology", "mm", "%", "anti", "warranty", "camera", "chip", "5g", "feature"],
  lifestyle: ["work", "cafe", "interior", "lifestyle", "space", "daily"],
  luxury: ["luxury", "premium", "elegant", "gold", "diamond", "high-end"],
  lookbook: ["lookbook", "collection", "fashion", "editorial", "style"]
};

function inputText(input: PosterInput): string {
  const parts = [
    input.industry,
    input.productName,
    input.productType,
    input.description,
    input.goal,
    input.mood,
    input.target,
    input.headline,
    input.subline1,
    input.subline2,
    input.price,
    ...(input.ingredients || [])
  ];
  return parts.filter(Boolean).join(" ").toLowerCase();
}

export function detectMechanism(input: PosterInput): MechanismResult {
  const scores: Record<Mechanism, number> = {
    ingredient: 0,
    offer: 0,
    emotion: 0,
    energy: 0,
    feature: 0,
    lifestyle: 0,
    luxury: 0,
    lookbook: 0
  };

  if (input.hasCollection || input.goal === "lookbook") scores.lookbook += 8;
  if ((input.ingredients || []).length > 0) scores.ingredient += 5;
  if (input.price) scores.offer += 4;
  if (input.goal === "viral") scores.energy += 4;
  if (input.goal === "trust") scores.feature += 3;
  if (input.goal === "brand") scores.emotion += 3;
  if (input.goal === "sale" || input.goal === "conversion") scores.offer += 2;

  const industry = (input.industry || "").toLowerCase();
  if (["beauty", "skincare", "cosmetics", "fmcg", "food", "beverage"].includes(industry)) {
    scores.ingredient += 1;
  }
  if (["restaurant", "food service", "buffet"].includes(industry)) {
    scores.offer += 2;
  }
  if (["health", "supplement", "tech", "electronics"].includes(industry)) {
    scores.feature += 2;
  }

  const text = inputText(input);
  for (const [mechanism, words] of Object.entries(KEYWORDS) as Array<[Mechanism, string[]]>) {
    for (const word of words) {
      if (text.includes(word)) {
        scores[mechanism] += 2;
      }
    }
  }

  const ranked = Object.entries(scores).sort((a, b) => b[1] - a[1]) as Array<[Mechanism, number]>;
  const primary: Mechanism = ranked[0][1] > 0 ? ranked[0][0] : "ingredient";
  const secondary: Mechanism | null = ranked[1][1] > 0 && ranked[1][0] !== primary ? ranked[1][0] : null;

  return { primary, secondary, scores };
}
