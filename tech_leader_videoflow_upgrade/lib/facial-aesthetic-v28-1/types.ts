import { z } from "zod";

export const FacialAestheticRequestSchema = z.object({
  brandName: z.string().min(1),
  industry: z.enum([
    "kol_beauty",
    "cosmetic_brand",
    "spa",
    "beauty_clinic",
    "wedding_studio",
    "tiktok_creator",
    "luxury_beauty"
  ]).default("cosmetic_brand"),
  targetAudience: z.string().default("Vietnamese women 22-35"),
  faceDescription: z.string().default("soft oval balanced face, high elegant nose bridge, almond eyes, soft natural lips"),
  makeupDirection: z.string().default("clean semi-matte K-beauty makeup, soft luxury contour, premium glow highlight"),
  commercialGoal: z.enum(["trust", "conversion", "luxury", "young_glow", "tiktok_beauty"]).default("conversion"),
  styleDna: z.array(z.string()).default([
    "Korean/Vietnamese beauty commerce",
    "soft femininity",
    "luxury beauty",
    "commercial trust",
    "TikTok beauty appeal"
  ]),
  saveWinnerDna: z.boolean().default(true)
});

export type FacialAestheticRequest = z.infer<typeof FacialAestheticRequestSchema>;

export type FacialBalanceProfile = {
  face_shape: string;
  harmony_rules: string[];
  proportion_logic: string[];
  commercial_realism_rules: string[];
};

export type NoseStructureProfile = {
  bridge: string;
  nose_tip: string;
  width: string;
  perception_mapping: Record<string, string>;
  anti_plastic_surgery_rules: string[];
};

export type ContourHighlightPlan = {
  highlight_zones: string[];
  contour_zones: string[];
  blush_zones: string[];
  reasoning: string[];
};

export type FacialDepthProfile = {
  depth_cues: string[];
  shadow_rules: string[];
  glow_rules: string[];
  perception_goal: string[];
};

export type BeautySymmetryProfile = {
  symmetry_level: string;
  natural_asymmetry_rules: string[];
  realism_rules: string[];
};

export type LuxuryFaceScore = {
  facial_balance_score: number;
  nose_elegance_score: number;
  jawline_softness_score: number;
  luxury_beauty_score: number;
  commercial_face_score: number;
  tiktok_beauty_score: number;
  final_score: number;
  passed: boolean;
};

export type FacialAestheticOutput = {
  face_dna: Record<string, unknown>;
  facial_balance: FacialBalanceProfile;
  nose_structure: NoseStructureProfile;
  contour_highlight: ContourHighlightPlan;
  facial_depth: FacialDepthProfile;
  beauty_symmetry: BeautySymmetryProfile;
  luxury_face_scoring: LuxuryFaceScore;
  beauty_perception_psychology: Record<string, string>;
  prompt_enhancer: string;
  negative_prompt: string;
  verification: Record<string, unknown>;
  winner_dna?: Record<string, unknown>;
};
