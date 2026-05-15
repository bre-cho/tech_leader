import {
  FACE_WIDTH_LOCK_NEGATIVE_TERMS,
  FACE_WIDTH_LOCK_REQUIRED_TERMS
} from "./faceBalanceProfiles";
import type { FaceBalanceScore } from "./types";

const has = (text: string, term: string) => text.toLowerCase().includes(term.toLowerCase());

function pct(prompt: string, terms: string[]): number {
  const found = terms.filter((term) => has(prompt, term)).length;
  return Math.round((found / Math.max(terms.length, 1)) * 100);
}

export function scoreFaceBalancePrompt(prompt: string, negativePrompt = ""): FaceBalanceScore {
  const issues: string[] = [];

  const uShapeTerms = [
    "soft rounded compact face",
    "soft U-shape face structure",
    "rounded lower face silhouette",
    "compact soft face geometry"
  ];

  const chinTerms = [
    "natural chin base width retention",
    "rounded blunt chin",
    "softly flattened chin tip",
    "smooth curved chin contour",
    "non-pointed chin structure"
  ];

  const jawTerms = [
    "softly widened jaw width",
    "soft lower-face width continuity",
    "gentle jaw width preservation",
    "balanced lower-face width distribution",
    "soft facial width transition"
  ];

  const cheekTerms = [
    "subtle youthful face roundness",
    "soft facial mass retention",
    "natural cheek width continuity",
    "soft cheek fullness",
    "subtle cheek volume"
  ];

  const missingRequired = FACE_WIDTH_LOCK_REQUIRED_TERMS.filter((term) => !has(prompt, term));
  if (missingRequired.length) issues.push(`Thiếu Face Width Lock: ${missingRequired.join(", ")}`);

  const missingNegatives = FACE_WIDTH_LOCK_NEGATIVE_TERMS.filter((term) => !has(negativePrompt, term));
  if (missingNegatives.length) issues.push(`Negative prompt thiếu: ${missingNegatives.slice(0, 10).join(", ")}`);

  const uShapeStructure = pct(prompt, uShapeTerms);
  const chinBaseWidth = pct(prompt, chinTerms);
  const jawWidthRetention = pct(prompt, jawTerms);
  const cheekFullness = pct(prompt, cheekTerms);
  const antiVLine = Math.max(0, 100 - missingNegatives.length * 4);

  const total = Math.round(
    uShapeStructure * 0.20 +
      chinBaseWidth * 0.25 +
      jawWidthRetention * 0.25 +
      cheekFullness * 0.15 +
      antiVLine * 0.15
  );

  return {
    uShapeStructure,
    chinBaseWidth,
    jawWidthRetention,
    cheekFullness,
    antiVLine,
    total,
    grade: total >= 90 ? "WINNER" : total >= 80 ? "GOOD" : total >= 70 ? "PASS" : "FAIL",
    issues
  };
}
