import type {
  FacialAestheticRequest,
  FacialBalanceProfile,
  NoseStructureProfile,
  ContourHighlightPlan,
  FacialDepthProfile,
  BeautySymmetryProfile,
  LuxuryFaceScore
} from "./types";

export function buildFacialAestheticPromptEnhancer(params: {
  req: FacialAestheticRequest;
  balance: FacialBalanceProfile;
  nose: NoseStructureProfile;
  contour: ContourHighlightPlan;
  depth: FacialDepthProfile;
  symmetry: BeautySymmetryProfile;
  scoring: LuxuryFaceScore;
}) {
  const { req, balance, nose, contour, depth, symmetry, scoring } = params;

  const prompt = `
FACIAL AESTHETIC PERCEPTION ENGINE:

Create a high-end Korean/Vietnamese beauty commerce face with:
- Face shape: ${balance.face_shape}
- Jawline: soft feminine jawline
- Nose: ${nose.bridge}; ${nose.nose_tip}; ${nose.width}
- Eyes: large bright almond eyes with trust-building catchlight
- Lips: soft natural full lips with realistic lip texture
- Skin: smooth glow realistic skin with micro texture
- Makeup base: clean semi-matte skin
- Contour: soft luxury contour
- Highlight: premium glow highlight on ${contour.highlight_zones.join(", ")}
- Nose contour: natural slim nose definition without fake plastic surgery look
- Blush: ${contour.blush_zones.join(", ")}

Facial depth:
${depth.depth_cues.join(", ")}

Symmetry:
${symmetry.symmetry_level}; allow natural human micro-asymmetry.

Beauty perception:
soft femininity, luxury beauty, young glow, commercial trust, TikTok beauty appeal.

Commercial realism:
not a perfect AI doll face; preserve believable high-end beauty advertising realism.
Target audience: ${req.targetAudience}.
Brand: ${req.brandName}.
`.trim();

  const negative = [
    "AI doll face",
    "perfect plastic symmetry",
    "fake plastic surgery look",
    "over-sharp nose",
    "overfilled lips",
    "plastic skin",
    "over-smoothing",
    "unrealistic facial proportions",
    "harsh contour",
    "oily highlight",
    "deformed eyes",
    "distorted nose",
    "aged harsh shadow",
    "low quality"
  ].join(", ");

  return { prompt, negative };
}
