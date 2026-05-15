import type { FacialAestheticRequest, NoseStructureProfile } from "./types";

export function analyzeNoseStructure(req: FacialAestheticRequest): NoseStructureProfile {
  const desc = req.faceDescription.toLowerCase();
  const highBridge = desc.includes("high") || desc.includes("cao") || desc.includes("sống mũi");

  return {
    bridge: highBridge ? "high elegant nose bridge with natural contour" : "soft refined natural nose bridge",
    nose_tip: "refined but natural nose tip",
    width: "balanced natural width, realistic for Vietnamese/Asian beauty",
    perception_mapping: {
      "high nose bridge": "elegance",
      "soft nose contour": "femininity",
      "refined nose tip": "luxury beauty",
      "balanced width": "realism",
      "natural shadow": "3D facial dimension"
    },
    anti_plastic_surgery_rules: [
      "enhance nose perception without fake surgery look",
      "avoid overly sharp artificial bridge",
      "avoid tiny unrealistic nose tip",
      "keep highlight and contour soft enough for commercial realism"
    ]
  };
}
