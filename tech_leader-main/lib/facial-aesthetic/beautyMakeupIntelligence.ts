import type { BeautyPersona, FaceObservation, PromptDNA } from "./facialAesthetic.types";

export function buildBeautyMakeupDNA(persona: BeautyPersona, observation: FaceObservation = {}): PromptDNA["makeup_intelligence"] {
  const isLuxury = persona.luxuryLevel >= 80;
  const isTikTok = persona.platform === "tiktok" || persona.platform === "shopee";

  return {
    base: isTikTok ? "clean semi-matte K-beauty skin with realistic glow" : "premium editorial semi-matte skin",
    contour: isLuxury ? "soft luxury contour with natural cheek depth" : "subtle natural contour",
    highlight: "premium glow on cheekbones, nose bridge, inner eye corners and chin, not oily",
    nose_contour: "natural slim nose definition, refined bridge highlight, no surgery look",
    blush: persona.softnessLevel > 85 ? "soft pink feminine warmth" : "muted peach warmth",
    lips: observation.lips ?? "soft natural full lips, hydrated rose tone, visible lip texture",
    eye_makeup: "clean feminine eyeliner, bright almond eyes, clear catchlights, soft lashes"
  };
}
