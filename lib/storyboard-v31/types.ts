import { z } from "zod";

export const PlatformSchema = z.enum(["youtube_shorts", "tiktok", "reels", "fashion_film", "ads"]);
export const ProviderSchema = z.enum(["veo", "runway", "kling", "ltx", "banana", "hidream", "comfyui"]);

export const ShotSpecSchema = z.object({
  id: z.number().int().positive(),
  phase: z.string().default("runway"),
  title: z.string().min(1),
  description: z.string().default(""),
  camera: z.string().default("medium"),
  lens: z.string().default("35mm"),
  movement: z.string().default("static"),
  durationSec: z.number().min(0.5).max(10).default(2.5),
  subjectFocus: z.string().default("model"),
  emotionBeat: z.string().default("anticipation"),
  continuityTags: z.array(z.string()).default([]),
  prompt: z.string().default(""),
  negativePrompt: z.string().default("")
});

export const StoryboardV31RequestSchema = z.object({
  title: z.string().default("Fashion Shorts Cinematic Storyboard"),
  concept: z.string().default("London Fashion Week cinematic runway short"),
  platform: PlatformSchema.default("youtube_shorts"),
  aspectRatio: z.string().default("9:16"),
  musicBpm: z.number().min(60).max(180).default(118),
  targetDurationSec: z.number().min(15).max(90).default(35),
  mainCharacter: z.string().default("same female fashion model"),
  location: z.string().default("London Fashion Week"),
  fashionDna: z.string().default("luxury editorial runway, black outfit, cinematic spotlight"),
  inputShots: z.array(ShotSpecSchema).default([]),
  autoGenerateIfEmpty: z.boolean().default(true),
  provider: z.object({
    image: ProviderSchema.default("hidream"),
    video: ProviderSchema.default("veo"),
    motionFallback: ProviderSchema.default("runway")
  }).default({}),
  outputDir: z.string().default("storage/v31-storyboard-rhythm"),
  saveTemplate: z.boolean().default(true)
});

export type ShotSpec = z.infer<typeof ShotSpecSchema>;
export type StoryboardV31Request = z.infer<typeof StoryboardV31RequestSchema>;

export type RhythmNode = {
  shotId: number;
  phase: string;
  energy: number;
  intimacy: number;
  motion: number;
  tension: number;
  payoff: number;
  facePriority: number;
  socialProof: number;
  hookType: string;
};

export type RetentionBeat = {
  startSec: number;
  endSec: number;
  role: string;
  requiredHook: string;
  targetEnergy: number;
};

export type V31Output = {
  status: "ready" | "blocked";
  request: StoryboardV31Request;
  shots: ShotSpec[];
  rhythmGraph: RhythmNode[];
  energyValidation: Record<string, unknown>;
  microHooks: Record<string, unknown>;
  cameraLanguage: Record<string, unknown>;
  runwayEscalation: Record<string, unknown>;
  socialProof: Record<string, unknown>;
  shortsTimeline: Record<string, unknown>;
  retentionValidation: Record<string, unknown>;
  providerPayloads: Record<string, unknown>;
  verification: Record<string, unknown>;
  artifacts: Record<string, unknown>[];
};
