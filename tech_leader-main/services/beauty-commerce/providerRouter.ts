import type { BeautyCommerceRequest } from "./beautyCommerceTypes";

export function routeBeautyProvider(req: BeautyCommerceRequest) {
  if (req.preferredProvider) {
    return {provider: req.preferredProvider, reason: "user_preference"};
  }

  if (req.references.length >= 2 || req.productName || req.channel === "billboard") {
    return {
      provider: "banana",
      reason: "commercial composition, multi-reference consistency, typography/product layout"
    };
  }

  if (req.industry === "luxury_beauty" || req.poseGoal === "editorial") {
    return {provider: "hidream", reason: "cinematic luxury and editorial composition"};
  }

  if (req.industry === "lingerie_fashion" || req.industry === "swimwear_fashion") {
    return {provider: "sdxl", reason: "controlled fashion workflow and pose/fabric control"};
  }

  return {provider: "banana", reason: "default commercial beauty provider"};
}
