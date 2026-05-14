import { z } from "zod";

export const BeautyPersonaSchema = z.object({
  agePerception: z.string().default("22-30"),
  archetype: z.string().default("soft Korean-Vietnamese beauty commerce"),
  platform: z.enum(["tiktok", "shopee", "instagram", "luxury_brand", "clinic", "wedding"]).default("tiktok"),
  conversionGoal: z.string().default("trust + softness + beauty aspiration"),
  realismLevel: z.number().min(0).max(100).default(88),
  luxuryLevel: z.number().min(0).max(100).default(82),
  softnessLevel: z.number().min(0).max(100).default(90),
  sensualityLevel: z.number().min(0).max(100).default(55)
});

export const FaceObservationSchema = z.object({
  faceShape: z.string().optional(),
  jawline: z.string().optional(),
  noseBridge: z.string().optional(),
  noseTip: z.string().optional(),
  eyes: z.string().optional(),
  lips: z.string().optional(),
  skin: z.string().optional(),
  lighting: z.string().optional(),
  pose: z.string().optional(),
  productPlacement: z.string().optional(),
  typography: z.string().optional(),
  notes: z.string().optional()
});

export const FacialAestheticRequestSchema = z.object({
  persona: BeautyPersonaSchema.optional(),
  observation: FaceObservationSchema.optional(),
  prompt: z.string().min(1).default("beauty commerce KOL portrait"),
  negativePrompt: z.string().optional(),
  provider: z.enum(["banana", "hidream", "flux", "sdxl", "auto"]).default("auto"),
  strictCommercialSafety: z.boolean().default(true)
});

export type BeautyPersona = z.infer<typeof BeautyPersonaSchema>;
export type FaceObservation = z.infer<typeof FaceObservationSchema>;
export type FacialAestheticRequest = z.infer<typeof FacialAestheticRequestSchema>;

export type ScoreKey =
  | "facial_balance_score"
  | "nose_elegance_score"
  | "jawline_softness_score"
  | "eye_trust_score"
  | "skin_glow_score"
  | "facial_depth_score"
  | "luxury_beauty_score"
  | "commercial_face_score"
  | "tiktok_beauty_score"
  | "conversion_readiness_score";

export type ScoreMap = Record<ScoreKey, number>;

export interface EngineSignal {
  id: string;
  label: string;
  score: number;
  evidence: string[];
  recommendation: string;
}

export interface VerificationIssue {
  severity: "reject" | "warning" | "info";
  code: string;
  message: string;
  fix: string;
}

export interface PromptDNA {
  identity_layer: Record<string, string | number>;
  facial_geometry: Record<string, string | number>;
  makeup_intelligence: Record<string, string | number>;
  commercial_psychology: Record<string, string | number>;
  negative_controls: string[];
}

export interface ProviderPayload {
  provider: "banana" | "hidream" | "flux" | "sdxl";
  prompt: string;
  negativePrompt: string;
  params: Record<string, string | number | boolean>;
}

export interface FacialAestheticResult {
  ok: boolean;
  scores: ScoreMap;
  signals: EngineSignal[];
  issues: VerificationIssue[];
  dna: PromptDNA;
  providerPayload: ProviderPayload;
  winnerDNA: {
    shouldStore: boolean;
    reason: string;
    tags: string[];
    finalScore: number;
  };
}
