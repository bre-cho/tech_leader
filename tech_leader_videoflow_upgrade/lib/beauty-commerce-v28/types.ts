import { z } from "zod";

export const ReferenceKindSchema = z.enum(["identity", "makeup", "fashion", "lighting", "pose", "product", "layout"]);
export const ProviderSchema = z.enum(["banana", "hidream", "flux", "sdxl", "comfyui", "veo", "ltx"]);

export const BeautyReferenceSchema = z.object({
  kind: ReferenceKindSchema,
  label: z.string().min(1),
  uri: z.string().optional(),
  base64: z.string().optional(),
  mimeType: z.string().default("image/png"),
  lockStrength: z.number().min(0).max(1).default(0.85),
  notes: z.string().optional()
});

export const BeautyCommerceInputSchema = z.object({
  brandName: z.string().min(1),
  productName: z.string().optional(),
  productType: z.string().optional(),
  industry: z.enum([
    "beauty_kol",
    "cosmetic_brand",
    "spa_kol",
    "beauty_clinic",
    "fashion_tryon",
    "livestream_kol",
    "tiktok_beauty_ads",
    "wedding_studio",
    "luxury_beauty"
  ]).default("tiktok_beauty_ads"),
  avatarDna: z.string().default("realistic Vietnamese/Asian beauty KOL, natural skin texture, soft feminine commercial look"),
  campaignGoal: z.enum(["conversion", "trust", "awareness", "product_demo", "livestream", "try_on"]).default("conversion"),
  channel: z.enum(["tiktok", "reels", "shorts", "livestream", "poster", "lookbook"]).default("tiktok"),
  references: z.array(BeautyReferenceSchema).default([]),
  sceneCount: z.number().min(3).max(12).default(5),
  durationSec: z.number().min(6).max(60).default(15),
  preferredProvider: ProviderSchema.optional(),
  outputDir: z.string().default("storage/beauty-commerce-v28"),
  saveWinnerDna: z.boolean().default(true),
  constraints: z.array(z.string()).default([])
});

export type BeautyCommerceInput = z.infer<typeof BeautyCommerceInputSchema>;
export type BeautyReference = z.infer<typeof BeautyReferenceSchema>;
export type ProviderName = z.infer<typeof ProviderSchema>;

export type EngineReport = {
  name: string;
  score: number;
  data: Record<string, unknown>;
  warnings: string[];
};

export type BeautyCommerceOutput = {
  status: "ready" | "blocked";
  input: BeautyCommerceInput;
  bananaMultiReference: EngineReport;
  femininityEngine: Record<string, EngineReport>;
  videoEngine: Record<string, EngineReport>;
  providerRoute: Record<string, unknown>;
  prompt: string;
  negativePrompt: string;
  videoPlan: Record<string, unknown>;
  verification: Record<string, unknown>;
  commercialScore: Record<string, unknown>;
  providerPayloads: Record<string, unknown>;
  artifacts: Array<Record<string, unknown>>;
  winnerDna?: Record<string, unknown>;
};
