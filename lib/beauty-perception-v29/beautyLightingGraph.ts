import type { BeautyPerceptionRequest, EngineResult, LightingStyle } from "./types";

const LIGHTING: Record<LightingStyle, Record<string, unknown>> = {
  DARK_EDITORIAL: {
    cues: ["narrow spotlight", "fast falloff", "hair shadow breakup", "face isolation"],
    perception: "luxury editorial mystery",
    provider: "HiDream"
  },
  KOREAN_SOFT: {
    cues: ["diffuse pastel light", "soft frontal fill", "low shadow", "light skin bloom"],
    perception: "TikTok/KOL commercial beauty",
    provider: "Nano Banana"
  },
  LIFESTYLE_REALISM: {
    cues: ["window light", "warm ambiance", "shallow DOF", "realistic skin"],
    perception: "parasocial trust",
    provider: "Nano Banana"
  },
  SUNSET_GLOW: {
    cues: ["warm backlight", "hair rim light", "golden skin warmth", "soft haze"],
    perception: "emotional warmth and romance",
    provider: "HiDream"
  },
  CINEMATIC_SPOTLIGHT: {
    cues: ["face spotlight", "deep shadow", "strong contrast", "isolated expression"],
    perception: "dramatic cinematic beauty",
    provider: "HiDream"
  },
  LUXURY_WINDOWLIGHT: {
    cues: ["large soft window", "gentle shadow", "premium skin texture", "neutral background"],
    perception: "high-end beauty realism",
    provider: "Nano Banana"
  }
};

export function buildBeautyLightingGraph(req: BeautyPerceptionRequest): EngineResult {
  const style = LIGHTING[req.lightingStyle];

  return {
    name: "BeautyLightingGraph",
    score: 94,
    data: {
      selected_style: req.lightingStyle,
      ...style,
      style_catalog: LIGHTING,
      rules: [
        "lighting must support skin realism and commercial perception",
        "avoid plastic over-smoothing",
        "keep eye catchlight visible",
        "use DOF and falloff to control attention"
      ]
    },
    warnings: []
  };
}
