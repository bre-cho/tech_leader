import type {
  FacialAestheticRequest,
  FacialBalanceProfile,
  NoseStructureProfile,
  ContourHighlightPlan,
  FacialDepthProfile,
  BeautySymmetryProfile,
  LuxuryFaceScore
} from "./types";

function clamp(n: number) {
  return Math.max(0, Math.min(100, Math.round(n)));
}

export function scoreLuxuryFace(params: {
  req: FacialAestheticRequest;
  balance: FacialBalanceProfile;
  nose: NoseStructureProfile;
  contour: ContourHighlightPlan;
  depth: FacialDepthProfile;
  symmetry: BeautySymmetryProfile;
}): LuxuryFaceScore {
  const { req, nose } = params;
  const desc = `${req.faceDescription} ${req.makeupDirection} ${req.styleDna.join(" ")}`.toLowerCase();

  const facial_balance_score = clamp(desc.includes("balanced") || desc.includes("cân đối") ? 94 : 88);
  const nose_elegance_score = clamp(nose.bridge.includes("high") || desc.includes("sống mũi cao") ? 92 : 86);
  const jawline_softness_score = clamp(desc.includes("soft") || desc.includes("mềm") ? 91 : 87);
  const luxury_beauty_score = clamp(desc.includes("luxury") || desc.includes("sang trọng") ? 95 : 89);
  const commercial_face_score = clamp(desc.includes("commercial") || desc.includes("commerce") || desc.includes("quảng cáo") ? 96 : 90);
  const tiktok_beauty_score = clamp(req.industry === "tiktok_creator" || req.commercialGoal === "tiktok_beauty" ? 94 : 90);

  const final_score = clamp(
    (facial_balance_score +
      nose_elegance_score +
      jawline_softness_score +
      luxury_beauty_score +
      commercial_face_score +
      tiktok_beauty_score) / 6
  );

  return {
    facial_balance_score,
    nose_elegance_score,
    jawline_softness_score,
    luxury_beauty_score,
    commercial_face_score,
    tiktok_beauty_score,
    final_score,
    passed: final_score >= 90
  };
}
