import { z } from "zod";

export const PlatformSchema = z.enum(["tiktok", "instagram", "livestream_thumbnail", "poster", "lookbook", "landing_page"]);
export const LightingStyleSchema = z.enum([
  "DARK_EDITORIAL",
  "KOREAN_SOFT",
  "LIFESTYLE_REALISM",
  "SUNSET_GLOW",
  "CINEMATIC_SPOTLIGHT",
  "LUXURY_WINDOWLIGHT"
]);

export const ReferenceKindSchema = z.enum([
  "identity_ref",
  "makeup_ref",
  "fashion_ref",
  "lighting_ref",
  "pose_ref",
  "gesture_ref",
  "hair_ref",
  "skin_ref",
  "product_ref"
]);

export const BeautyReferenceSchema = z.object({
  kind: ReferenceKindSchema,
  label: z.string().min(1),
  uri: z.string().optional(),
  base64: z.string().optional(),
  mimeType: z.string().default("image/png"),
  lockStrength: z.number().min(0).max(1).default(0.9),
  notes: z.string().optional()
});

export const BeautyPerceptionRequestSchema = z.object({
  brandName: z.string().min(1),
  campaignName: z.string().default("beauty_perception_campaign"),
  productName: z.string().optional(),
  platform: PlatformSchema.default("tiktok"),
  targetAudience: z.string().default("Vietnamese/Asian women 18-35 interested in beauty and fashion"),
  identityDna: z.object({
    faceGeometry: z.string().default("soft oval balanced face"),
    eyeRatio: z.string().default("large bright almond eyes"),
    lipRatio: z.string().default("natural lips, slightly fuller lower lip"),
    noseSoftness: z.string().default("soft refined nose bridge"),
    eyebrowCurvature: z.string().default("natural thin straight eyebrows"),
    skinTone: z.string().default("light neutral-warm Asian skin"),
    moleMap: z.string().optional(),
    aegyoSal: z.string().default("soft natural aegyo-sal"),
    jawSoftness: z.string().default("soft feminine jawline"),
    hairTexture: z.string().default("long dark hair with natural shine"),
    smileSignature: z.string().default("micro warm smile")
  }).default({}),
  desiredSignals: z.array(z.string()).default([
    "direct eye contact",
    "slight smile",
    "head tilt",
    "collarbone elegance",
    "soft hair framing",
    "warm backlight",
    "shallow DOF",
    "finger near lips"
  ]),
  lightingStyle: LightingStyleSchema.default("KOREAN_SOFT"),
  references: z.array(BeautyReferenceSchema).default([]),
  sceneCount: z.number().min(1).max(12).default(5),
  outputDir: z.string().default("storage/v29-beauty-perception"),
  saveMemory: z.boolean().default(true)
});

export type BeautyPerceptionRequest = z.infer<typeof BeautyPerceptionRequestSchema>;
export type LightingStyle = z.infer<typeof LightingStyleSchema>;

export type EngineResult<T = Record<string, unknown>> = {
  name: string;
  score: number;
  data: T;
  warnings: string[];
};

export type GraphNode = {
  id: string;
  type: string;
  label: string;
  score?: number;
  properties: Record<string, unknown>;
};

export type GraphEdge = {
  from: string;
  to: string;
  relation: string;
  weight: number;
  reasoning: string;
};

export type BeautyPerceptionGraph = {
  graph_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export type BeautyPerceptionOutput = {
  status: "ready" | "blocked";
  request: BeautyPerceptionRequest;
  graph: BeautyPerceptionGraph;
  engines: Record<string, EngineResult>;
  commercialBeautyScore: Record<string, unknown>;
  socialCtrPrediction: Record<string, unknown>;
  sceneSpec: Record<string, unknown>;
  providerRoute: Record<string, unknown>;
  promptPack: Record<string, unknown>;
  verification: Record<string, unknown>;
  artifacts: Record<string, unknown>[];
  memoryDna?: Record<string, unknown>;
};
