import type { StoryboardV31Request } from "@/lib/storyboard-v31/types";
import type { DesignStudioRequest, DesignStudioResponse } from "@/lib/design/pipeline-api";

type ProviderName = StoryboardV31Request["provider"]["image"];

const providerNames: ProviderName[] = ["veo", "runway", "kling", "ltx", "banana", "hidream", "comfyui"];

function toProviderName(value: unknown, fallback: ProviderName): ProviderName {
  if (typeof value !== "string") {
    return fallback;
  }
  const normalized = value.toLowerCase().trim();
  return providerNames.includes(normalized as ProviderName) ? (normalized as ProviderName) : fallback;
}

function platformFromChannel(channel: string): StoryboardV31Request["platform"] {
  const lower = channel.toLowerCase();
  if (lower.includes("tiktok")) {
    return "tiktok";
  }
  if (lower.includes("reels")) {
    return "reels";
  }
  if (lower.includes("short")) {
    return "youtube_shorts";
  }
  if (lower.includes("fashion")) {
    return "fashion_film";
  }
  return "ads";
}

function numberFromUnknown(value: unknown, fallback: number): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const parsed = Number(value.replace(/[^\d.]/g, ""));
    if (Number.isFinite(parsed) && parsed > 0) {
      return parsed;
    }
  }
  return fallback;
}

function readSceneText(scene: Record<string, unknown>, keys: string[], fallback: string): string {
  for (const key of keys) {
    const value = scene[key];
    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }
  return fallback;
}

function mapShots(storyboard: Array<Record<string, unknown>>): StoryboardV31Request["inputShots"] {
  return storyboard.slice(0, 18).map((scene, index) => {
    const id = index + 1;
    return {
      id,
      phase: readSceneText(scene, ["phase"], index < 2 ? "hook" : "runway"),
      title: readSceneText(scene, ["title", "scene", "shot"], `Scene ${id}`),
      description: readSceneText(scene, ["description", "prompt", "copy"], "Retention-focused cinematic shot"),
      camera: readSceneText(scene, ["camera", "camera_move"], "medium"),
      lens: readSceneText(scene, ["lens"], "35mm"),
      movement: readSceneText(scene, ["motion", "action"], "glide"),
      durationSec: numberFromUnknown(scene.duration, 2.5),
      subjectFocus: readSceneText(scene, ["subject_focus", "subject"], "model"),
      emotionBeat: readSceneText(scene, ["emotion", "emotion_beat"], "confidence"),
      continuityTags: ["identity_lock", "wardrobe_lock", "lighting_lock"],
      prompt: readSceneText(scene, ["prompt", "description"], "fashion cinematic runway shot"),
      negativePrompt: "identity drift, bad anatomy, plastic skin, continuity break",
    };
  });
}

function pickProviderFromContract(result: DesignStudioResponse): {
  image: ProviderName;
  video: ProviderName;
  motionFallback: ProviderName;
} {
  const contract = result.best_concept?.provider_contract;
  const preferredModels =
    contract && typeof contract === "object" && Array.isArray((contract as Record<string, unknown>).preferred_models)
      ? ((contract as Record<string, unknown>).preferred_models as unknown[])
      : [];

  const firstModel = preferredModels.find((item) => typeof item === "string") ?? null;
  const videoPreview = result.video_concept_preview;
  const videoFromPreview =
    videoPreview && typeof videoPreview === "object"
      ? (videoPreview as Record<string, unknown>).provider
      : null;

  return {
    image: toProviderName(firstModel, "hidream"),
    video: toProviderName(videoFromPreview, "veo"),
    motionFallback: "runway",
  };
}

export function buildV31RequestFromPipeline(
  brief: DesignStudioRequest,
  result: DesignStudioResponse,
): StoryboardV31Request {
  const providers = pickProviderFromContract(result);
  const inputShots = mapShots(result.storyboard ?? []);
  const totalDuration = inputShots.reduce((sum, shot) => sum + shot.durationSec, 0);

  return {
    title: `${brief.brand_name || "Brand"} Retention Rhythm Storyboard`,
    concept: result.best_concept?.headline || result.best_concept?.prompt || brief.product,
    platform: platformFromChannel(brief.channel),
    aspectRatio: "9:16",
    musicBpm: 118,
    targetDurationSec: Math.max(20, Math.min(60, Math.round(totalDuration) || 35)),
    mainCharacter: "same female fashion model",
    location: "fashion commercial set",
    fashionDna:
      "luxury editorial runway, cinematic spotlight, retention-optimized energy curve, identity continuity",
    inputShots,
    autoGenerateIfEmpty: true,
    provider: providers,
    outputDir: `storage/v31-storyboard-rhythm/${result.workflow_id}`,
    saveTemplate: true,
  };
}
