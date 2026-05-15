import type { BeautyIdentityRuntimeRequest, RuntimeReport } from "./types";

export function runIdentityBeautyQualityGate(params: {
  req: BeautyIdentityRuntimeRequest;
  identityDna: RuntimeReport;
  faceLockContract: RuntimeReport;
  visualRecipe: RuntimeReport;
  promptPack: RuntimeReport;
}): RuntimeReport {
  const { req, identityDna, faceLockContract, promptPack } = params;
  const prompt = String((promptPack.data as any).prompt ?? "");
  const negative = String((promptPack.data as any).negativePrompt ?? "");

  const checks = {
    has_face_reference_or_text_dna: req.references.some(r => r.kind === "face") || identityDna.score >= 85,
    face_lock_enabled: req.faceLock.enabled,
    face_lock_strict_enough: req.faceLock.strictness >= 0.9,
    prompt_contains_identity_lock: prompt.includes("FACE LOCK PRIORITY"),
    prompt_preserves_skin_texture: prompt.toLowerCase().includes("visible pores") || prompt.toLowerCase().includes("skin texture"),
    negative_blocks_identity_drift: negative.includes("identity drift"),
    negative_blocks_plastic_skin: negative.includes("plastic skin"),
    negative_blocks_bad_hands: negative.includes("deformed hands"),
    has_provider_payload: Boolean((promptPack.data as any).providerPayload),
    commercial_safety_rules: prompt.toLowerCase().includes("commercial photography")
  };

  const score = Math.round(Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 100);

  return {
    name: "IdentityBeautyQualityGate",
    score,
    data: {
      passed: score >= 90,
      checks,
      production_rules: [
        "ALWAYS preserve eye spacing",
        "NEVER alter nose bridge structure",
        "keep lips natural",
        "preserve cheek proportions",
        "avoid over-smoothing",
        "preserve subtle facial asymmetry",
        "keep skin pores visible",
        "use realistic hand anatomy",
        "maintain realistic fabric physics",
        "prioritize realism over stylization"
      ]
    },
    warnings: Object.entries(checks).filter(([, v]) => !v).map(([k]) => `failed_check:${k}`)
  };
}
