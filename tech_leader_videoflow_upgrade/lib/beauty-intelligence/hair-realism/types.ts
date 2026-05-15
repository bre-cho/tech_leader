export type BeautyProvider = "sdxl" | "flux" | "hidream" | "veo" | "runway" | "kling" | "generic";

export type HairSceneType =
  | "hero portrait"
  | "overhead carpet shot"
  | "mirror reflection scene"
  | "runway spotlight scene"
  | "beauty macro shot"
  | "window sunlight portrait"
  | "fashion cardigan movement shot"
  | "pastel vanity lifestyle scene"
  | "cream sofa cinematic shot"
  | "close-up eye contact beauty portrait"
  | string;

export type StoryboardHairScene = {
  scene_id: number;
  scene_type: HairSceneType;
  camera: string;
  lighting: string;
  prompt: string;
  negative_prompt: string;
  hair_realism_lock: string[];
};

export type HairRealismScore = {
  strandSeparation: number;
  fiberTexture: number;
  babyHair: number;
  flyawayHair: number;
  lightingPhysics: number;
  foregroundSharpness: number;
  antiPlasticHair: number;
  total: number;
  grade: "FAIL" | "PASS" | "GOOD" | "WINNER";
  issues: string[];
};

export type EnhanceHairPromptInput = {
  sceneId?: number;
  basePrompt: string;
  negativePrompt?: string;
  provider?: BeautyProvider;
  sceneType?: HairSceneType;
  camera?: string;
  lighting?: string;
  strictGate?: boolean;
};

export type EnhanceHairPromptOutput = {
  prompt: string;
  negativePrompt: string;
  score: HairRealismScore;
  appliedModules: string[];
  provider: BeautyProvider;
  gatePassed: boolean;
};
