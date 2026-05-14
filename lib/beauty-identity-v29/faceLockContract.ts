import type { BeautyIdentityRuntimeRequest, RuntimeReport } from "./types";

export function buildFaceLockContract(req: BeautyIdentityRuntimeRequest): RuntimeReport {
  const contract = {
    priority: "ULTRA IMPORTANT — FACE LOCK PRIORITY",
    enabled: req.faceLock.enabled,
    strictness: req.faceLock.strictness,
    must_preserve: [
      "exact eye shape",
      "exact nose structure",
      "exact lip shape",
      "exact cheek proportions",
      "exact jawline",
      "exact facial spacing",
      "exact eyebrow structure",
      "exact skin tone",
      "exact facial identity",
      "exact beauty proportions",
      "exact facial realism",
      "natural asymmetry",
      req.faceLock.preserveMoleMap ? "mole/skin-detail map" : "general skin identity"
    ],
    forbidden: [
      "face morphing",
      "identity drift",
      "changing ethnicity",
      "changing facial geometry",
      "exaggerated anime beauty",
      "over-editing",
      "AI plastic skin",
      "doll face",
      "unrealistic eye enlargement"
    ],
    qa_thresholds: {
      face_lock_score_min: 92,
      skin_realism_min: 88,
      eye_consistency_min: 90,
      mouth_nose_consistency_min: 90,
      hand_anatomy_min: 85
    }
  };

  return {
    name: "FaceLockContract",
    score: req.faceLock.enabled ? Math.round(req.faceLock.strictness * 100) : 60,
    data: contract,
    warnings: req.faceLock.enabled ? [] : ["Face lock disabled."]
  };
}
