import type { FacialAestheticRequest, FacialBalanceProfile } from "./types";

export function analyzeFacialBalance(req: FacialAestheticRequest): FacialBalanceProfile {
  const desc = req.faceDescription.toLowerCase();

  const faceShape =
    desc.includes("round") || desc.includes("tròn") ? "soft round face with balanced contour" :
    desc.includes("heart") || desc.includes("trái tim") ? "soft heart-shaped face" :
    desc.includes("long") || desc.includes("dài") ? "soft long oval correction" :
    "soft oval balanced face";

  return {
    face_shape: faceShape,
    harmony_rules: [
      "balanced forehead, cheekbone, jawline and chin relationship",
      "eyes must remain naturally aligned and friendly",
      "lips should feel natural, not overfilled",
      "jawline should be soft feminine, not harsh or overly sharp"
    ],
    proportion_logic: [
      "high-end beauty commercial realism, not AI doll perfection",
      "slight natural asymmetry is allowed for realism",
      "avoid over-smoothed and over-symmetrical beauty filter look",
      "facial features should support trust, softness and premium beauty"
    ],
    commercial_realism_rules: [
      "retain natural skin texture",
      "avoid fake plastic surgery look",
      "beauty should feel aspirational but believable",
      "suitable for cosmetics, spa, clinic, wedding and TikTok beauty commerce"
    ]
  };
}
