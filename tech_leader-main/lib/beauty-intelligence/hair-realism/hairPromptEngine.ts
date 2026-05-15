import { getProviderHairBooster } from "./providerHairAdapters";
import { GLOBAL_HAIR_NEGATIVE_PROMPT, GLOBAL_HAIR_POSITIVE_PROMPT, STORYBOARD_160_HAIR_REALISM_SCENES } from "./storyboard160";
import { scoreHairRealismPrompt } from "./hairScoring";
import type { EnhanceHairPromptInput, EnhanceHairPromptOutput } from "./types";

function uniq(parts: string[]): string[] {
  return Array.from(new Set(parts.map((p) => p.trim()).filter(Boolean)));
}

export function findStoryboardHairScene(sceneId?: number) {
  if (!sceneId) return undefined;
  return STORYBOARD_160_HAIR_REALISM_SCENES.find((scene) => scene.scene_id === sceneId);
}

export function enhanceScenePromptWithHairRealism(input: EnhanceHairPromptInput): EnhanceHairPromptOutput {
  const provider = input.provider ?? "generic";
  const storyboardScene = findStoryboardHairScene(input.sceneId);

  const contextParts = [
    input.basePrompt,
    storyboardScene?.scene_type || input.sceneType || "",
    storyboardScene?.camera || input.camera || "",
    storyboardScene?.lighting || input.lighting || "",
    GLOBAL_HAIR_POSITIVE_PROMPT,
    ...(storyboardScene?.hair_realism_lock ?? []),
    ...getProviderHairBooster(provider)
  ];

  const prompt = uniq(contextParts).join(", ");
  const negativePrompt = uniq([input.negativePrompt || "", GLOBAL_HAIR_NEGATIVE_PROMPT]).join(", ");
  const score = scoreHairRealismPrompt(prompt, negativePrompt);
  const gatePassed = input.strictGate ? score.total >= 80 : true;

  return {
    prompt,
    negativePrompt,
    score,
    provider,
    appliedModules: [
      "STORYBOARD_160_SCENES_MASTER_HAIR_REALISM_V2",
      "GLOBAL_HAIR_POSITIVE_PROMPT",
      "CORE_HAIR_REALISM_COMBO",
      `PROVIDER_${provider.toUpperCase()}_HAIR_BOOSTER`
    ],
    gatePassed
  };
}
