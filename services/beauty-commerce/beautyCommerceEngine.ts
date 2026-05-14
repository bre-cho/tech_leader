import { BeautyCommerceRequestSchema, type BeautyCommerceResponse } from "./beautyCommerceTypes";
import { buildBeautyAttentionRouting } from "./attentionRouting";
import { buildFemininityPerception } from "./femininityPerception";
import { scoreLuxuryBeautyInputs } from "./luxuryBeautyScoring";
import { buildPosePsychology } from "./posePsychology";
import { buildEyeContactPlan } from "./eyeContactEngine";
import { buildFashionSilhouette } from "./fashionSilhouette";
import { buildSoftSensualCommercialLogic } from "./softSensualCommercialLogic";
import { predictBeautyConversion } from "./beautyConversionPrediction";
import { routeBeautyProvider } from "./providerRouter";
import { compileBeautyCommercePrompt } from "./beautyPromptCompiler";
import { verifyBeautyCommerce } from "./verification";
import { buildBeautyWinnerDna, saveBeautyWinnerDna } from "./winnerDna";

export function runBeautyCommerceEngine(raw: unknown): BeautyCommerceResponse {
  const req = BeautyCommerceRequestSchema.parse(raw);

  const attentionRouting = buildBeautyAttentionRouting(req);
  const femininityPerception = buildFemininityPerception(req);
  const luxuryBeautyScoring = scoreLuxuryBeautyInputs(req);
  const posePsychology = buildPosePsychology(req);
  const eyeContact = buildEyeContactPlan(req);
  const fashionSilhouette = buildFashionSilhouette(req);
  const softSensualCommercialLogic = buildSoftSensualCommercialLogic(req);
  const beautyConversionPrediction = predictBeautyConversion(req, luxuryBeautyScoring);
  const providerRoute = routeBeautyProvider(req);

  const partial = {
    attentionRouting,
    femininityPerception,
    luxuryBeautyScoring,
    posePsychology,
    eyeContact,
    fashionSilhouette,
    softSensualCommercialLogic,
    beautyConversionPrediction,
    providerRoute
  };

  const {prompt, negativePrompt} = compileBeautyCommercePrompt(req, partial);

  const decision = {
    ...partial,
    prompt,
    negativePrompt
  };

  const verification = verifyBeautyCommerce(decision);
  const commercialScore = {
    final_score: Math.round((Number(luxuryBeautyScoring.final_score) + Number(verification.score)) / 2),
    input_score: luxuryBeautyScoring,
    verification_score: verification.score,
    pass: verification.passed && luxuryBeautyScoring.pass
  };

  const providerPayload = {
    provider: providerRoute.provider,
    reason: providerRoute.reason,
    prompt,
    negativePrompt,
    references: req.references,
    outputDir: req.outputDir,
    handoff:
      providerRoute.provider === "banana"
        ? "/api/providers/google-banana/commercial-poster"
        : providerRoute.provider === "hidream"
          ? "/api/v1/hidream/commercial-visual/generate"
          : providerRoute.provider === "sdxl"
            ? "/api/providers/comfyui/sdxl-fashion"
            : "/api/providers/image/generate"
  };

  let winnerDna: Record<string, unknown> | undefined;
  if (req.saveWinnerDna && commercialScore.final_score >= 90) {
    winnerDna = buildBeautyWinnerDna(req, decision, verification);
    saveBeautyWinnerDna(winnerDna);
  }

  return {
    status: commercialScore.pass ? "ready" : "blocked",
    decision,
    verification,
    commercialScore,
    winnerDna,
    providerPayload
  };
}
