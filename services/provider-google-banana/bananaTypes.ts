import { z } from "zod";

export const BananaModelSchema = z.enum([
  "gemini-3.1-flash-image-preview",
  "gemini-3-pro-image-preview",
  "gemini-2.5-flash-image"
]);

export const BananaModeSchema = z.enum([
  "generate",
  "edit",
  "multi_reference",
  "commercial_poster",
  "tiktok_creative",
  "upscale_8k"
]);

export const BananaImageInputSchema = z.object({
  mimeType: z.string().default("image/png"),
  dataBase64: z.string().min(10),
  label: z.string().optional()
});

export type BananaImageInput = z.infer<typeof BananaImageInputSchema>;

export const BananaRequestSchema = z.object({
  mode: BananaModeSchema.default("generate"),
  model: BananaModelSchema.default("gemini-3.1-flash-image-preview"),
  prompt: z.string().min(3),
  negativePrompt: z.string().optional(),
  aspectRatio: z.string().default("4:5"),
  resolution: z.enum(["1K", "2K", "4K"]).default("2K"),
  outputDir: z.string().default("storage/google-banana"),
  images: z.array(BananaImageInputSchema).default([]),
  metadata: z.record(z.any()).default({}),
  safety: z.object({
    requireCommercialSafe: z.boolean().default(true),
    rejectUnreadableText: z.boolean().default(true),
    preserveBrandAssets: z.boolean().default(true)
  }).default({})
});

export type BananaRequest = z.infer<typeof BananaRequestSchema>;

export type BananaArtifact = {
  artifactId: string;
  type: "image" | "text" | "manifest";
  path: string;
  mimeType: string;
  sizeBytes: number;
  checksumSha256: string;
  provider: "google-banana";
  model: string;
  metadata: Record<string, unknown>;
};

export type BananaResponse = {
  status: "succeeded" | "failed";
  mode: string;
  model: string;
  textParts: string[];
  artifacts: BananaArtifact[];
  scoring: Record<string, unknown>;
  winnerDnaCandidate?: Record<string, unknown>;
  rawUsage?: Record<string, unknown>;
};
