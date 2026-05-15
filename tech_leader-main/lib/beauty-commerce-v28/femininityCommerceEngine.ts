import type { BeautyCommerceInput } from "./types";
import { runEyeContactEngine } from "./eyeContactEngine";
import { runSmileNaturalizationEngine } from "./smileNaturalizationEngine";
import { runSoftFemininityScoring } from "./softFemininityScoring";
import { runCommercialBeautyPoseEngine } from "./commercialBeautyPoseEngine";
import { runTikTokBeautyCompositionEngine } from "./tiktokBeautyCompositionEngine";
import { runLuxurySkinLightingEngine } from "./luxurySkinLightingEngine";
import { runBodyBalanceEngine } from "./bodyBalanceEngine";
import { runSoftNecklinePerception } from "./softNecklinePerception";
import { runBeautyAttentionRouting } from "./beautyAttentionRouting";

export function runFemininityBeautyCommerceEngine(input: BeautyCommerceInput) {
  return {
    eyeContact: runEyeContactEngine(input),
    smileNaturalization: runSmileNaturalizationEngine(input),
    softFemininity: runSoftFemininityScoring(input),
    commercialPose: runCommercialBeautyPoseEngine(input),
    tiktokComposition: runTikTokBeautyCompositionEngine(input),
    luxurySkinLighting: runLuxurySkinLightingEngine(input),
    bodyBalance: runBodyBalanceEngine(input),
    softNeckline: runSoftNecklinePerception(input),
    beautyAttentionRouting: runBeautyAttentionRouting(input)
  };
}
