import { z } from "zod";
import { STORYBOARD_PROVIDERS } from "@/lib/contracts/providerContract";

export const StoryboardFormatSchema = z.enum(["fashion_runway", "beauty_campaign", "product_launch", "event_film", "custom"]);
export const PhaseSchema = z.enum(["setup", "backstage", "runway", "after_party"]);
export const ProviderSchema = z.enum(STORYBOARD_PROVIDERS);

export const StoryboardRequestSchema = z.object({
  title: z.string().min(1).default("London Fashion Week Storyboard"),
  format: StoryboardFormatSchema.default("fashion_runway"),
  mainCharacter: z.string().default("1 cô gái / female fashion model"),
  location: z.string().default("London Fashion Week"),
  aspectRatio: z.string().default("1:1"),
  totalShots: z.number().min(12).max(240).default(160),
  targetDurationSec: z.number().min(30).max(900).default(240),
  requestedPhases: z.array(PhaseSchema).default(["setup", "backstage", "runway", "after_party"]),
  identityDna: z.object({
    faceLock: z.boolean().default(true),
    wardrobeContinuity: z.boolean().default(true),
    hairMakeupContinuity: z.boolean().default(true),
    characterNotes: z.string().default("same female model, cinematic editorial beauty identity")
  }).default({}),
  style: z.object({
    mood: z.string().default("cinematic high-fashion, dramatic runway, luxury editorial"),
    lighting: z.string().default("London overcast city light, backstage tungsten, runway spotlights, after party neon"),
    cameraLanguage: z.string().default("establishing shots, close-ups, inserts, tracking, slow motion, flycam, reaction shots"),
    colorGrade: z.string().default("luxury fashion contrast, clean skin tones, controlled highlights")
  }).default({}),
  providers: z.object({
    still: ProviderSchema.default("hidream"),
    video: ProviderSchema.default("veo"),
    motionAlt: ProviderSchema.default("runway")
  }).default({}),
  outputDir: z.string().default("storage/v30-storyboard-agent"),
  saveAsTemplate: z.boolean().default(true)
});

export type StoryboardRequest = z.infer<typeof StoryboardRequestSchema>;
export type PhaseName = z.infer<typeof PhaseSchema>;

export type ShotSpec = {
  id: number;
  phase: PhaseName;
  title: string;
  description: string;
  camera: string;
  lens: string;
  movement: string;
  durationSec: number;
  subjectFocus: string;
  emotionBeat: string;
  continuityTags: string[];
  prompt: string;
  negativePrompt: string;
  providerPayload: Record<string, unknown>;
};

export type PhasePlan = {
  phase: PhaseName;
  title: string;
  startShot: number;
  endShot: number;
  purpose: string;
  retentionRole: string;
  shots: ShotSpec[];
};

export type StoryboardOutput = {
  status: "ready" | "blocked";
  request: StoryboardRequest;
  analysis: Record<string, unknown>;
  phases: PhasePlan[];
  timeline: Record<string, unknown>;
  providerPayloads: Record<string, unknown>;
  verification: Record<string, unknown>;
  artifacts: Record<string, unknown>[];
};
