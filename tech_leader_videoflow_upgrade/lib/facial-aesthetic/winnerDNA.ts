import type { ScoreMap } from "./facialAesthetic.types";
import { avg } from "./utils";

export function finalBeautyCommerceScore(scores: ScoreMap): number {
  return avg([
    scores.facial_balance_score,
    scores.nose_elegance_score,
    scores.eye_trust_score,
    scores.skin_glow_score,
    scores.luxury_beauty_score,
    scores.commercial_face_score * 1.15,
    scores.conversion_readiness_score * 1.2
  ]);
}

export function buildWinnerDNA(scores: ScoreMap, tags: string[]) {
  const finalScore = finalBeautyCommerceScore(scores);
  return {
    shouldStore: finalScore >= 88 && scores.commercial_face_score >= 85,
    reason:
      finalScore >= 88
        ? "High facial aesthetic + commercial beauty conversion score; eligible for Winner DNA memory."
        : "Not enough commercial certainty; keep as candidate, do not promote yet.",
    tags,
    finalScore
  };
}
