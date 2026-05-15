import { z } from "zod";

export const VideoFlowLayerTypeSchema = z.enum(["text", "image", "video", "audio", "caption", "shape", "group"]);

export const VideoFlowTimelineLayerSchema = z.object({
  id: z.string().min(1),
  type: VideoFlowLayerTypeSchema,
  track: z.number().int().min(0).default(0),
  startSec: z.number().min(0),
  durationSec: z.number().positive(),
  zIndex: z.number().int().default(0),
  props: z.record(z.unknown()).default({}),
  source: z.string().optional(),
  prompt: z.string().optional(),
  metadata: z.record(z.unknown()).default({})
});

export const VideoFlowTimelineSchema = z.object({
  engine: z.literal("videoflow"),
  version: z.string().default("1.2.1-local-adapter"),
  name: z.string().min(1),
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  fps: z.number().int().min(12).max(120).default(30),
  durationSec: z.number().positive(),
  backgroundColor: z.string().default("#050505"),
  aspectRatio: z.string().default("9:16"),
  layers: z.array(VideoFlowTimelineLayerSchema),
  renderHints: z.object({
    renderer: z.enum(["server", "browser", "dom", "provider-preview"]).default("provider-preview"),
    outputFormat: z.enum(["mp4", "webm", "json"]).default("mp4"),
    safeZone: z.boolean().default(true),
    subtitleBurnIn: z.boolean().default(true),
    providerClipMerge: z.boolean().default(true)
  }).default({}),
  provenance: z.object({
    source: z.string().default("tech_leader_storyboard"),
    adapter: z.string().default("VideoFlowStoryboardAdapter"),
    createdAt: z.string(),
    inputHash: z.string().optional()
  })
});

export type VideoFlowTimelineLayer = z.infer<typeof VideoFlowTimelineLayerSchema>;
export type VideoFlowTimeline = z.infer<typeof VideoFlowTimelineSchema>;
