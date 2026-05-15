import { FacialAestheticRequestSchema, type FacialAestheticOutput } from "./types";
import { analyzeFacialBalance } from "./facialBalance";
import { analyzeNoseStructure } from "./noseStructure";
import { buildContourHighlightReasoning } from "./contourReasoning";
import { buildFacialDepthProfile } from "./facialDepthEngine";
import { analyzeBeautySymmetry } from "./beautySymmetry";
import { scoreLuxuryFace } from "./luxuryFaceScoring";
import { buildBeautyPerceptionPsychology } from "./beautyPsychology";
import { buildFacialAestheticPromptEnhancer } from "./promptEnhancer";
import { verifyFacialAesthetic } from "./verification";
import { buildFacialAestheticWinnerDna, saveFacialAestheticWinnerDna } from "./winnerDna";

export function runFacialAestheticEngine(raw: unknown): FacialAestheticOutput {
  const req = FacialAestheticRequestSchema.parse(raw);

  const facial_balance = analyzeFacialBalance(req);
  const nose_structure = analyzeNoseStructure(req);
  const contour_highlight = buildContourHighlightReasoning(req);
  const facial_depth = buildFacialDepthProfile(req);
  const beauty_symmetry = analyzeBeautySymmetry(req);
  const luxury_face_scoring = scoreLuxuryFace({
    req,
    balance: facial_balance,
    nose: nose_structure,
    contour: contour_highlight,
    depth: facial_depth,
    symmetry: beauty_symmetry
  });
  const beauty_perception_psychology = buildBeautyPerceptionPsychology();
  const prompt = buildFacialAestheticPromptEnhancer({
    req,
    balance: facial_balance,
    nose: nose_structure,
    contour: contour_highlight,
    depth: facial_depth,
    symmetry: beauty_symmetry,
    scoring: luxury_face_scoring
  });

  const face_dna = {
    face_shape: "soft oval balanced face",
    jawline: "soft feminine jawline",
    nose: nose_structure.bridge,
    eyes: "large bright almond eyes",
    lips: "soft natural full lips",
    skin: "smooth glow realistic skin",
    makeup: {
      base: "clean semi-matte skin",
      contour: "soft luxury contour",
      highlight: "premium glow highlight",
      nose_contour: "natural slim nose definition",
      blush: "soft pink feminine warmth"
    },
    beauty_perception: [
      "soft femininity",
      "luxury beauty",
      "young glow",
      "commercial trust",
      "TikTok beauty appeal"
    ]
  };

  const partial = {
    face_dna,
    facial_balance,
    nose_structure,
    contour_highlight,
    facial_depth,
    beauty_symmetry,
    luxury_face_scoring,
    beauty_perception_psychology,
    prompt_enhancer: prompt.prompt,
    negative_prompt: prompt.negative
  };

  const verification = verifyFacialAesthetic(partial);

  let output: FacialAestheticOutput = {
    ...partial,
    verification
  };

  if (req.saveWinnerDna && luxury_face_scoring.passed && verification.passed) {
    const winner_dna = buildFacialAestheticWinnerDna(req, output);
    saveFacialAestheticWinnerDna(winner_dna);
    output = { ...output, winner_dna };
  }

  return output;
}
