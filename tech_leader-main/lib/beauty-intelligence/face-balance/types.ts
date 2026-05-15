export type FaceBalanceProvider = "sdxl" | "flux" | "hidream" | "veo" | "runway" | "kling" | "generic";

export type FaceBalanceInput = {
  basePrompt: string;
  negativePrompt?: string;
  provider?: FaceBalanceProvider;
  strictGate?: boolean;
};

export type FaceBalanceScore = {
  uShapeStructure: number;
  chinBaseWidth: number;
  jawWidthRetention: number;
  cheekFullness: number;
  antiVLine: number;
  total: number;
  grade: "FAIL" | "PASS" | "GOOD" | "WINNER";
  issues: string[];
};

export type FaceBalanceOutput = {
  prompt: string;
  negativePrompt: string;
  score: FaceBalanceScore;
  gatePassed: boolean;
  appliedModules: string[];
};
