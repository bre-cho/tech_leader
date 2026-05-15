import type { BeautyCommerceDecision } from "./beautyCommerceTypes";

export function verifyBeautyCommerce(decision: BeautyCommerceDecision) {
  const checks = {
    has_attention_routing: Array.isArray((decision.attentionRouting as any).route),
    has_femininity_perception: Boolean(decision.femininityPerception),
    has_luxury_scoring: Boolean((decision.luxuryBeautyScoring as any).final_score),
    has_pose_psychology: Boolean((decision.posePsychology as any).posture),
    has_eye_contact: Boolean((decision.eyeContact as any).sequence),
    has_fashion_silhouette: Boolean((decision.fashionSilhouette as any).fabricPhysics),
    has_soft_sensual_safety: Boolean((decision.softSensualCommercialLogic as any).disallowedFrame),
    has_conversion_prediction: Boolean((decision.beautyConversionPrediction as any).predicted_ctr_percent),
    prompt_is_commercial_safe: decision.prompt.includes("tasteful") && decision.negativePrompt.includes("explicit nudity")
  };
  const score = Math.round(Object.values(checks).filter(Boolean).length / Object.values(checks).length * 100);
  return {
    passed: score >= 90,
    score,
    checks,
    issues: Object.entries(checks).filter(([, v]) => !v).map(([k]) => k)
  };
}
