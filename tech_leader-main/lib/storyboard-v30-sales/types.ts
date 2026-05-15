import { z } from "zod";

export const ProductCategorySchema = z.enum([
  "beauty",
  "lipstick",
  "skincare",
  "fashion",
  "fmcg",
  "sauce",
  "drink",
  "seasoning",
  "fitness",
  "product",
  "unknown"
]);

export const SalesMechanismSchema = z.enum([
  "lip_desire",
  "skin_transformation",
  "sun_shield",
  "ingredient_explosion",
  "liquid_vortex",
  "texture_proof",
  "luxury_identity",
  "human_emotion",
  "mini_world_story",
  "product_dominance"
]);

export const SalesStoryboardInputSchema = z.object({
  enabled: z.boolean().default(true),
  productName: z.string().min(1),
  category: z.string().optional(),
  brief: z.string().optional(),
  posterPrompt: z.string().optional(),
  goal: z.enum(["sale", "premium", "trust", "viral", "launch"]).default("sale"),
  platform: z.enum(["tiktok", "reels", "shorts", "meta", "runway_film"]).default("shorts"),
  duration: z.union([z.literal(15), z.literal(30)]).default(15),
  aspectRatio: z.string().default("9:16"),
  language: z.enum(["vi", "en"]).default("vi"),
  preserveIdentity: z.boolean().default(true),
  preserveProductShape: z.boolean().default(true),
  styleHint: z.string().optional(),
  constraints: z.array(z.string()).default([])
});

export const V30SalesRequestSchema = z.object({
  salesEngine: SalesStoryboardInputSchema.optional()
});

export type ProductCategory = z.infer<typeof ProductCategorySchema>;
export type SalesMechanism = z.infer<typeof SalesMechanismSchema>;
export type SalesStoryboardInput = z.infer<typeof SalesStoryboardInputSchema>;

export type SalesDecision = {
  category: ProductCategory;
  mechanism: SalesMechanism;
  visualHook: string;
  storyArc: "hook_desire_trust_cta" | "problem_solution_proof_cta" | "luxury_aura_reveal_cta";
  pacing: "fast" | "balanced" | "cinematic";
  priority: string[];
  reason: string[];
};

export type SalesScene = {
  sceneId: string;
  order: number;
  startSec: number;
  endSec: number;
  durationSec: number;
  scenePurpose: "hook" | "desire" | "trust" | "proof" | "cta" | "luxury_aura";
  visual: string;
  action: string;
  camera: string;
  lighting: string;
  motion: string;
  overlayText?: string;
  voiceover?: string;
  retentionNote: string;
};

export type SalesProviderPrompt = {
  sceneId: string;
  provider: "veo" | "runway" | "kling" | "seedance" | "banana" | "hidream";
  prompt: string;
  negativePrompt: string;
  settings: Record<string, unknown>;
};

export type SalesStoryboardScore = {
  hookStrength: number;
  productClarity: number;
  desire: number;
  trust: number;
  conversion: number;
  retention: number;
  risk: number;
  finalScore: number;
  verdict: "REBUILD" | "TEST" | "READY";
  reasons: string[];
};

export type SalesStoryboardOutput = {
  engineVersion: "auto_storyboard_engine_v3_sales_for_v30";
  input: SalesStoryboardInput;
  decision: SalesDecision;
  scenes: SalesScene[];
  providerPrompts: SalesProviderPrompt[];
  score: SalesStoryboardScore;
  exportJson: Record<string, unknown>;
};
