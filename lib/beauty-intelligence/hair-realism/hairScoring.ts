import { HAIR_REALISM_NEGATIVE_TERMS, HAIR_REALISM_POSITIVE_MODULES, HAIR_REALISM_REQUIRED_TERMS } from "./hairProfiles";
import type { HairRealismScore } from "./types";

function has(text: string, term: string): boolean {
  return text.toLowerCase().includes(term.toLowerCase());
}

function moduleScore(prompt: string, terms: string[]): number {
  const found = terms.filter((term) => has(prompt, term)).length;
  return Math.round((found / Math.max(terms.length, 1)) * 100);
}

export function scoreHairRealismPrompt(prompt: string, negativePrompt = ""): HairRealismScore {
  const issues: string[] = [];
  const requiredMissing = HAIR_REALISM_REQUIRED_TERMS.filter((term) => !has(prompt, term));
  if (requiredMissing.length > 0) {
    issues.push(`Thiếu combo tóc thật bắt buộc: ${requiredMissing.join(", ")}`);
  }

  const negativeMissing = HAIR_REALISM_NEGATIVE_TERMS.filter((term) => !has(negativePrompt, term));
  if (negativeMissing.length > 0) {
    issues.push(`Negative prompt thiếu bộ chống tóc lỗi: ${negativeMissing.slice(0, 10).join(", ")}`);
  }

  const strandSeparation = moduleScore(prompt, HAIR_REALISM_POSITIVE_MODULES.strandSeparation);
  const fiberTexture = has(prompt, "visible natural hair fiber texture") ? 100 : 0;
  const babyHair = moduleScore(prompt, HAIR_REALISM_POSITIVE_MODULES.babyHair);
  const flyawayHair = moduleScore(prompt, HAIR_REALISM_POSITIVE_MODULES.flyawayHair);
  const lightingPhysics = moduleScore(prompt, HAIR_REALISM_POSITIVE_MODULES.lightingPhysics);
  const foregroundSharpness = moduleScore(prompt, HAIR_REALISM_POSITIVE_MODULES.lensSharpness);
  const antiPlasticHair = Math.max(0, 100 - negativeMissing.length * 6);

  const total = Math.round(
    strandSeparation * 0.18 +
      fiberTexture * 0.14 +
      babyHair * 0.16 +
      flyawayHair * 0.12 +
      lightingPhysics * 0.18 +
      foregroundSharpness * 0.12 +
      antiPlasticHair * 0.10
  );

  return {
    strandSeparation,
    fiberTexture,
    babyHair,
    flyawayHair,
    lightingPhysics,
    foregroundSharpness,
    antiPlasticHair,
    total,
    grade: total >= 90 ? "WINNER" : total >= 80 ? "GOOD" : total >= 70 ? "PASS" : "FAIL",
    issues
  };
}
