import type { FacialAestheticRequest, VerificationIssue, ScoreMap } from "./facialAesthetic.types";

export function verifyFacialAesthetic(request: FacialAestheticRequest, scores: ScoreMap): VerificationIssue[] {
  const issues: VerificationIssue[] = [];
  const text = `${request.prompt} ${request.negativePrompt ?? ""}`.toLowerCase();

  const rejectTerms = [
    ["plastic surgery", "Mũi/phần mặt dễ bị cảm giác phẫu thuật giả."],
    ["doll face", "Gương mặt quá AI doll làm giảm commercial trust."],
    ["oversexualized", "Pose quá sexy có thể giảm trust trong beauty commerce."]
  ];

  for (const [term, message] of rejectTerms) {
    if (text.includes(term)) {
      issues.push({
        severity: request.strictCommercialSafety ? "reject" : "warning",
        code: `TERM_${term.toUpperCase().replace(/\s+/g, "_")}`,
        message,
        fix: "Dùng natural realism, soft elegance, safe commercial attractiveness."
      });
    }
  }

  for (const [key, value] of Object.entries(scores)) {
    if (value < 70) {
      issues.push({
        severity: "warning",
        code: `LOW_${key.toUpperCase()}`,
        message: `${key} thấp: ${value}/100`,
        fix: "Tăng soft lighting, facial harmony, product clarity và commercial hierarchy."
      });
    }
  }

  if (scores.commercial_face_score < 78 || scores.conversion_readiness_score < 80) {
    issues.push({
      severity: "warning",
      code: "LOW_CONVERSION_READINESS",
      message: "Ảnh có thể đẹp nhưng chưa đủ logic bán hàng.",
      fix: "Thêm product-in-hand, benefit hierarchy, clear CTA area, eye-contact-to-product routing."
    });
  }

  return issues;
}
