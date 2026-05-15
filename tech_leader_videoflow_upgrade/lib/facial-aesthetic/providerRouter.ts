import type { FacialAestheticRequest, ProviderPayload, PromptDNA } from "./facialAesthetic.types";
import { joinPrompt } from "./utils";

export function routeProvider(request: FacialAestheticRequest, dna: PromptDNA): ProviderPayload {
  const provider =
    request.provider !== "auto"
      ? request.provider
      : request.persona?.platform === "luxury_brand"
        ? "hidream"
        : request.prompt.toLowerCase().includes("typography")
          ? "banana"
          : "flux";

  const prompt = joinPrompt([
    request.prompt,
    "ultra realistic commercial beauty portrait",
    "soft Korean-Vietnamese beauty commerce aesthetic",
    String(dna.facial_geometry.face_shape),
    String(dna.facial_geometry.nose),
    String(dna.facial_geometry.eyes),
    String(dna.makeup_intelligence.base),
    String(dna.makeup_intelligence.contour),
    String(dna.makeup_intelligence.highlight),
    String(dna.commercial_psychology.attention_routing),
    "8K ultra high resolution, premium beauty advertising, realistic micro skin texture"
  ]);

  const negativePrompt = joinPrompt([
    request.negativePrompt,
    "AI doll face, plastic skin, over-smoothed skin, fake surgery nose, pinched nose, harsh contour",
    "oversized eyes, deformed face, distorted hands, bad anatomy, low quality, watermark, unreadable text",
    "cheap glamour, oversexualized pose, cluttered layout, flat lighting"
  ]);

  const params = {
    aspect_ratio: "4:5",
    guidance: provider === "sdxl" ? 7 : 5,
    realism_strength: 0.88,
    beauty_commerce_strength: 0.92,
    typography_control: provider === "banana",
    seed_locked: true
  };

  return { provider, prompt, negativePrompt, params };
}
