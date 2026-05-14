import {
  BeautyPersonaSchema,
  FacialAestheticRequestSchema,
  type FacialAestheticRequest,
  type FacialAestheticResult,
  type PromptDNA,
  type ScoreMap
} from "./facialAesthetic.types";
import { evaluateFacialBalance } from "./facialBalance";
import { evaluateNoseStructure } from "./noseStructure";
import { evaluateContourHighlight } from "./contourReasoning";
import { evaluateFacialDepth } from "./facialDepthEngine";
import { evaluateBeautySymmetry } from "./beautySymmetry";
import { evaluateLuxuryFace } from "./luxuryFaceScoring";
import { evaluateCommercialFace } from "./commercialFaceScoring";
import { buildBeautyMakeupDNA } from "./beautyMakeupIntelligence";
import { routeProvider } from "./providerRouter";
import { verifyFacialAesthetic } from "./verificationEngine";
import { buildWinnerDNA } from "./winnerDNA";
import { avg } from "./utils";

export function analyzeFacialAesthetic(input: Partial<FacialAestheticRequest>): FacialAestheticResult {
  const request = FacialAestheticRequestSchema.parse(input);
  const persona = BeautyPersonaSchema.parse(request.persona ?? {});
  const observation = request.observation ?? {};

  const signals = [
    evaluateFacialBalance(persona, observation),
    evaluateNoseStructure(observation),
    evaluateContourHighlight(observation),
    evaluateFacialDepth(observation),
    evaluateBeautySymmetry(observation),
    evaluateLuxuryFace(persona, observation),
    evaluateCommercialFace(persona, observation)
  ];

  const byId = Object.fromEntries(signals.map((s) => [s.id, s.score]));

  const scores: ScoreMap = {
    facial_balance_score: byId.facial_balance ?? 0,
    nose_elegance_score: byId.nose_structure ?? 0,
    jawline_softness_score: avg([byId.facial_balance ?? 0, persona.softnessLevel]),
    eye_trust_score: avg([byId.commercial_face ?? 0, persona.softnessLevel, 90]),
    skin_glow_score: byId.contour_highlight ?? 0,
    facial_depth_score: byId.facial_depth ?? 0,
    luxury_beauty_score: byId.luxury_face ?? 0,
    commercial_face_score: byId.commercial_face ?? 0,
    tiktok_beauty_score: avg([byId.commercial_face ?? 0, persona.platform === "tiktok" ? 94 : 84, persona.softnessLevel]),
    conversion_readiness_score: avg([
      byId.commercial_face ?? 0,
      byId.luxury_face ?? 0,
      byId.facial_balance ?? 0,
      byId.contour_highlight ?? 0
    ])
  };

  const dna: PromptDNA = {
    identity_layer: {
      age_perception: persona.agePerception,
      beauty_archetype: persona.archetype,
      platform: persona.platform,
      conversion_goal: persona.conversionGoal,
      realism_level: persona.realismLevel,
      luxury_level: persona.luxuryLevel
    },
    facial_geometry: {
      face_shape: observation.faceShape ?? "soft oval balanced face, natural commercial realism",
      jawline: observation.jawline ?? "soft feminine jawline, no sharp AI chin",
      nose: observation.noseBridge ?? "high elegant nose bridge with natural contour and refined nose tip",
      eyes: observation.eyes ?? "large bright almond eyes, warm eye contact, clear catchlights",
      lips: observation.lips ?? "soft natural full lips, healthy rose tone, visible lip texture",
      skin: observation.skin ?? "smooth glow realistic skin with micro texture, no plastic skin"
    },
    makeup_intelligence: buildBeautyMakeupDNA(persona, observation),
    commercial_psychology: {
      attention_routing: "face and eyes first, smile second, product-in-hand third, headline and benefits next",
      femininity: "soft feminine attraction, approachable aspiration, safe commercial attractiveness",
      luxury_signal: "clean premium beauty, restraint, editorial spacing, gold/champagne micro highlights",
      trust_bridge: "human-product linkage, warm KOL recommendation, visible product clarity"
    },
    negative_controls: [
      "AI doll face",
      "plastic skin",
      "fake surgery nose",
      "oversized eyes",
      "sharp unnatural chin",
      "harsh contour",
      "oversexualized pose",
      "cluttered layout"
    ]
  };

  const providerPayload = routeProvider({ ...request, persona }, dna);
  const issues = verifyFacialAesthetic({ ...request, persona }, scores);
  const ok = !issues.some((i) => i.severity === "reject");
  const winnerDNA = buildWinnerDNA(scores, [
    persona.platform,
    "beauty-commerce",
    "facial-aesthetic",
    "soft-luxury",
    "k-beauty"
  ]);

  return { ok, scores, signals, issues, dna, providerPayload, winnerDNA };
}

export * from "./facialAesthetic.types";
