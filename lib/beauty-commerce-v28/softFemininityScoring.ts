import type { BeautyCommerceInput, EngineReport } from "./types";

export function runSoftFemininityScoring(input: BeautyCommerceInput): EngineReport {
  const text = `${input.avatarDna} ${input.industry} ${input.channel}`.toLowerCase();
  const signals = {
    softLighting: /soft|warm|glow|pastel|luxury/.test(text),
    beautyContext: /beauty|kol|cosmetic|spa|wedding|fashion/.test(text),
    commercialSafe: !/explicit|nude|fetish/.test(text),
    productPurpose: Boolean(input.productName) || input.campaignGoal !== "conversion"
  };
  const score = Math.round(Object.values(signals).filter(Boolean).length / Object.keys(signals).length * 100);
  return {
    name: "SoftFemininityScoring",
    score,
    data: {
      signals,
      perceptionMap: {
        "soft shoulder angle": "femininity",
        "collarbone highlight": "elegance",
        "soft warm lighting": "emotional comfort",
        "shallow DOF": "luxury perception",
        "natural skin texture": "trust"
      },
      rule: "Commercial beauty attractiveness, not explicit sexualization."
    },
    warnings: score < 90 ? ["Soft femininity score below winner threshold; add lighting/fashion/commercial trust cues."] : []
  };
}
