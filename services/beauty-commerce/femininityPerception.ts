import type { BeautyCommerceRequest } from "./beautyCommerceTypes";

export function buildFemininityPerception(req: BeautyCommerceRequest) {
  const base = {
    softness: ["soft lighting", "natural skin texture", "relaxed facial expression"],
    confidence: ["upright posture", "calm eye contact", "controlled hand gesture"],
    elegance: ["clean negative space", "premium fabric texture", "balanced silhouette"],
    safety: ["adult fashion context", "no explicit nudity", "no fetish framing", "no exaggerated anatomy"]
  };

  if (req.poseGoal === "wedding_emotion") {
    return {...base, emotionalTone: "romantic softness, graceful bridal confidence"};
  }
  if (req.poseGoal === "spa_trust") {
    return {...base, emotionalTone: "calm wellness, healthy skin trust"};
  }
  if (req.poseGoal === "editorial") {
    return {...base, emotionalTone: "high-fashion editorial confidence"};
  }
  return {...base, emotionalTone: "soft feminine commercial confidence"};
}
