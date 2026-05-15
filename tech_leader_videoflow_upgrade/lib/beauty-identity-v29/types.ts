import { z } from "zod";

export const VisualIntentSchema = z.enum([
  "luxury_tropical_cafe",
  "korean_street_fashion",
  "sporty_wildcats_campaign",
  "luxury_lipstick_ad",
  "cinematic_car_wash",
  "custom"
]);

export const ProviderSchema = z.enum(["banana", "hidream", "flux", "sdxl_comfy", "auto"]);
export const PlatformSchema = z.enum(["poster", "tiktok", "instagram", "lookbook", "product_ad", "video_keyframe"]);

export const IdentityReferenceSchema = z.object({
  id: z.string().min(1),
  kind: z.enum(["face", "makeup", "hair", "fashion", "pose", "lighting", "product", "scene"]),
  uri: z.string().optional(),
  base64: z.string().optional(),
  mimeType: z.string().default("image/png"),
  lockStrength: z.number().min(0).max(1).default(0.92),
  notes: z.string().optional()
});

export const BeautyIdentityRuntimeRequestSchema = z.object({
  brandName: z.string().min(1),
  campaignName: z.string().default("beauty_identity_campaign"),
  visualIntent: VisualIntentSchema.default("luxury_tropical_cafe"),
  platform: PlatformSchema.default("poster"),
  provider: ProviderSchema.default("auto"),
  references: z.array(IdentityReferenceSchema).default([]),
  product: z.object({
    name: z.string().optional(),
    category: z.string().optional(),
    requiredLabelText: z.string().optional()
  }).default({}),
  faceLock: z.object({
    enabled: z.boolean().default(true),
    strictness: z.number().min(0).max(1).default(0.96),
    preserveMoleMap: z.boolean().default(true),
    preserveSkinTexture: z.boolean().default(true),
    preserveNaturalAsymmetry: z.boolean().default(true)
  }).default({}),
  output: z.object({
    aspectRatio: z.string().default("4:5"),
    quality: z.enum(["2K", "4K", "8K", "12K"]).default("8K"),
    outputDir: z.string().default("storage/v29-1-identity-lock")
  }).default({}),
  customPrompt: z.string().optional(),
  constraints: z.array(z.string()).default([]),
  saveWinnerDna: z.boolean().default(true)
});

export type BeautyIdentityRuntimeRequest = z.infer<typeof BeautyIdentityRuntimeRequestSchema>;
export type IdentityReference = z.infer<typeof IdentityReferenceSchema>;

export type RuntimeReport<T = Record<string, unknown>> = {
  name: string;
  score: number;
  data: T;
  warnings: string[];
};

export type BeautyIdentityRuntimeOutput = {
  status: "ready" | "blocked";
  request: BeautyIdentityRuntimeRequest;
  identityDna: RuntimeReport;
  faceLockContract: RuntimeReport;
  visualRecipe: RuntimeReport;
  providerRoute: RuntimeReport;
  promptPack: RuntimeReport;
  qaReport: RuntimeReport;
  providerPayloads: Record<string, unknown>;
  artifacts: Record<string, unknown>[];
  winnerDna?: Record<string, unknown>;
};
