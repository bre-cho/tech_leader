import {
  FACE_BALANCE_PROVIDER_BOOSTERS,
  FACE_WIDTH_LOCK_NEGATIVE_TERMS,
  FACE_WIDTH_LOCK_POSITIVE_TERMS
} from "./faceBalanceProfiles";
import { scoreFaceBalancePrompt } from "./faceBalanceScoring";
import type { FaceBalanceInput, FaceBalanceOutput, FaceBalanceProvider } from "./types";

const uniq = (parts: string[]) => Array.from(new Set(parts.map((p) => p.trim()).filter(Boolean)));

export function enhancePromptWithFaceWidthLock(input: FaceBalanceInput): FaceBalanceOutput {
  const provider: FaceBalanceProvider = input.provider || "generic";
  const providerBoosters = FACE_BALANCE_PROVIDER_BOOSTERS[provider] || FACE_BALANCE_PROVIDER_BOOSTERS.generic;

  const cleanedBasePrompt = input.basePrompt
    .replace(/soft compact oval face shape/gi, "soft rounded compact face")
    .replace(/oval face/gi, "soft rounded compact face");

  const prompt = uniq([cleanedBasePrompt, ...FACE_WIDTH_LOCK_POSITIVE_TERMS, ...providerBoosters]).join(", ");
  const negativePrompt = uniq([input.negativePrompt || "", ...FACE_WIDTH_LOCK_NEGATIVE_TERMS]).join(", ");
  const score = scoreFaceBalancePrompt(prompt, negativePrompt);

  return {
    prompt,
    negativePrompt,
    score,
    gatePassed: input.strictGate ? score.total >= 80 : true,
    appliedModules: [
      "MASTER_FACE_BALANCE_SYSTEM_V5",
      "FACE_WIDTH_LOCK",
      "CHIN_BASE_WIDTH_RETENTION",
      "ANTI_AI_V_LINE_NEGATIVE_PROMPT",
      `PROVIDER_${provider.toUpperCase()}_FACE_BOOSTER`
    ]
  };
}
