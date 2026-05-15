import { createHash } from "crypto";
import type { ShotSpec, V31Output } from "@/lib/storyboard-v31/types";
import { VideoFlowTimelineSchema, type VideoFlowTimeline, type VideoFlowTimelineLayer } from "./types";

const RATIO_SIZE: Record<string, { width: number; height: number }> = {
  "9:16": { width: 1080, height: 1920 },
  "16:9": { width: 1920, height: 1080 },
  "1:1": { width: 1080, height: 1080 },
  "4:5": { width: 1080, height: 1350 }
};

function hashInput(value: unknown): string {
  return createHash("sha256").update(JSON.stringify(value)).digest("hex");
}

function getCanvas(aspectRatio: string): { width: number; height: number } {
  return RATIO_SIZE[aspectRatio] ?? RATIO_SIZE["9:16"];
}

function accumulateStartSec(shots: ShotSpec[], index: number): number {
  return Number(shots.slice(0, index).reduce((sum, shot) => sum + shot.durationSec, 0).toFixed(3));
}

function shotToLayers(shot: ShotSpec, index: number, startSec: number, concept: string): VideoFlowTimelineLayer[] {
  const baseMeta = {
    shotId: shot.id,
    phase: shot.phase,
    title: shot.title,
    camera: shot.camera,
    lens: shot.lens,
    movement: shot.movement,
    emotionBeat: shot.emotionBeat,
    continuityTags: shot.continuityTags
  };

  return [
    {
      id: `shot_${shot.id}_video_placeholder`,
      type: "video",
      track: 0,
      startSec,
      durationSec: shot.durationSec,
      zIndex: index,
      prompt: shot.prompt || `${concept}. ${shot.description}`,
      props: {
        fit: "cover",
        transitionIn: index === 0 ? "fade" : "cut",
        transitionOut: "cut",
        camera: shot.camera,
        lens: shot.lens,
        movement: shot.movement
      },
      metadata: { ...baseMeta, role: "provider_clip_slot" }
    },
    {
      id: `shot_${shot.id}_caption`,
      type: "caption",
      track: 2,
      startSec: Number((startSec + Math.min(0.15, shot.durationSec / 10)).toFixed(3)),
      durationSec: Number(Math.max(0.5, shot.durationSec - 0.3).toFixed(3)),
      zIndex: 100 + index,
      props: {
        text: shot.title,
        position: [0.5, 0.82],
        maxWidth: 0.82,
        fontSizeEm: 4.2,
        fontWeight: 800,
        safeZone: true,
        shadow: "soft cinematic subtitle shadow"
      },
      metadata: { ...baseMeta, role: "safe_zone_caption" }
    }
  ];
}

export function compileStoryboardToVideoFlow(input: V31Output): VideoFlowTimeline {
  const { width, height } = getCanvas(input.request.aspectRatio);
  const layers = input.shots.flatMap((shot, index) => shotToLayers(
    shot,
    index,
    accumulateStartSec(input.shots, index),
    input.request.concept
  ));

  const requestedDuration = input.request.targetDurationSec;
  const shotDuration = input.shots.reduce((sum, shot) => sum + shot.durationSec, 0);
  const durationSec = Number(Math.max(requestedDuration, shotDuration).toFixed(3));

  const timeline = {
    engine: "videoflow" as const,
    version: "1.2.1-local-adapter",
    name: input.request.title,
    width,
    height,
    fps: 30,
    durationSec,
    backgroundColor: "#050505",
    aspectRatio: input.request.aspectRatio,
    layers,
    renderHints: {
      renderer: "provider-preview" as const,
      outputFormat: "mp4" as const,
      safeZone: true,
      subtitleBurnIn: true,
      providerClipMerge: true
    },
    provenance: {
      source: "storyboard-v31",
      adapter: "VideoFlowStoryboardAdapter",
      createdAt: new Date().toISOString(),
      inputHash: hashInput({ request: input.request, shots: input.shots })
    }
  };

  return VideoFlowTimelineSchema.parse(timeline);
}
