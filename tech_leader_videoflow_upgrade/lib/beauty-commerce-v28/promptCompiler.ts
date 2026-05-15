import type { BeautyCommerceInput } from "./types";

export function compileBeautyCommercePrompt(input: BeautyCommerceInput, engines: any, videoPlan: any) {
  const prompt = `
V28.2 + V28.3 Beauty Commerce Intelligence Output.

Brand: ${input.brandName}
Product: ${input.productName ?? "beauty/fashion brand visual"}
Product type: ${input.productType ?? "not specified"}
Industry: ${input.industry}
Channel: ${input.channel}
Campaign goal: ${input.campaignGoal}

Avatar DNA:
${input.avatarDna}

Banana Multi-Reference Rules:
${engines.bananaMultiReference.data.promptInjection}

Commercial Beauty Psychology:
- Eyes looking camera → trust
- Slight smile → friendliness
- Soft shoulder angle → femininity
- Collarbone highlight → elegance
- Neckline framing → attention routing
- Soft warm lighting → emotional comfort
- Shallow DOF → luxury perception

V28.2 Femininity Engine:
${JSON.stringify(engines.femininityEngine, null, 2)}

V28.3 Social Beauty Video Engine:
${JSON.stringify(engines.videoEngine, null, 2)}

Video Plan:
${JSON.stringify(videoPlan, null, 2)}

Generate a tasteful commercial beauty/KOL creative with realistic adult model, natural skin texture, clear face identity, soft luxury lighting, commercial-safe fashion styling, product/brand purpose, natural pose, eye contact, subtle smile and attention-routing composition.

The output must feel like social beauty commerce, not explicit adult content.
`.trim();

  const negativePrompt = [
    "explicit nudity",
    "sexual act",
    "fetish pose",
    "voyeuristic angle",
    "underage",
    "unrealistic anatomy",
    "over-inflated proportions",
    "plastic skin",
    "frozen smile",
    "dead eyes",
    "random gesture",
    "broken hands",
    "distorted product",
    "unreadable text",
    "wrong logo",
    "low quality",
    "static robotic presenter"
  ].join(", ");

  return { prompt, negativePrompt };
}
