import { z } from "zod";

export const BeautyIndustrySchema = z.enum([
  "personal_beauty",
  "kol_beauty",
  "studio_makeup",
  "wedding_studio",
  "spa",
  "fashion_brand",
  "cosmetic_brand",
  "beauty_clinic",
  "tiktok_creator",
  "lingerie_fashion",
  "swimwear_fashion",
  "luxury_beauty"
]);

export const ProviderSchema = z.enum(["banana", "hidream", "flux", "sdxl", "comfyui"]);

export const BeautyCommerceRequestSchema = z.object({
  brandName: z.string().min(1),
  productName: z.string().optional(),
  productType: z.string().optional(),
  industry: BeautyIndustrySchema.default("cosmetic_brand"),
  targetAudience: z.string().default("Vietnamese women 22-35"),
  campaignGoal: z.enum(["conversion", "awareness", "trust", "luxury_branding", "product_showcase"]).default("conversion"),
  channel: z.enum(["tiktok", "instagram", "facebook", "landing_page", "billboard", "lookbook"]).default("tiktok"),
  avatarDescription: z.string().default("virtual Asian beauty KOL, realistic natural skin texture"),
  outfitStyle: z.string().default("elegant luxury fashion styling"),
  poseGoal: z.enum(["confidence", "soft_feminine", "editorial", "product_demo", "wedding_emotion", "spa_trust"]).default("confidence"),
  sensualityLevel: z.enum(["none", "soft", "fashion_editorial"]).default("soft"),
  references: z.array(z.object({
    label: z.string(),
    uri: z.string().optional(),
    base64: z.string().optional(),
    mimeType: z.string().default("image/png")
  })).default([]),
  preferredProvider: ProviderSchema.optional(),
  outputDir: z.string().default("storage/v28-beauty-commerce"),
  saveWinnerDna: z.boolean().default(true),
  constraints: z.array(z.string()).default([])
});

export type BeautyCommerceRequest = z.infer<typeof BeautyCommerceRequestSchema>;

export type BeautyCommerceDecision = {
  attentionRouting: Record<string, unknown>;
  femininityPerception: Record<string, unknown>;
  luxuryBeautyScoring: Record<string, unknown>;
  posePsychology: Record<string, unknown>;
  eyeContact: Record<string, unknown>;
  fashionSilhouette: Record<string, unknown>;
  softSensualCommercialLogic: Record<string, unknown>;
  beautyConversionPrediction: Record<string, unknown>;
  providerRoute: Record<string, unknown>;
  prompt: string;
  negativePrompt: string;
};

export type BeautyCommerceResponse = {
  status: "ready" | "blocked";
  decision: BeautyCommerceDecision;
  verification: Record<string, unknown>;
  commercialScore: Record<string, unknown>;
  winnerDna?: Record<string, unknown>;
  providerPayload: Record<string, unknown>;
};
