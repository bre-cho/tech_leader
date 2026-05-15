import type { VideoFlowTimeline } from "./types";

export type VideoFlowVerification = {
  passed: boolean;
  score: number;
  checks: Record<string, boolean>;
  warnings: string[];
};

export function verifyVideoFlowTimeline(timeline: VideoFlowTimeline): VideoFlowVerification {
  const sorted = [...timeline.layers].sort((a, b) => a.startSec - b.startSec);
  const warnings: string[] = [];
  const checks = {
    hasLayers: timeline.layers.length > 0,
    hasVisualTrack: timeline.layers.some((layer) => layer.type === "video" || layer.type === "image"),
    hasCaptionTrack: timeline.layers.some((layer) => layer.type === "caption" || layer.type === "text"),
    noNegativeStart: timeline.layers.every((layer) => layer.startSec >= 0),
    noZeroDuration: timeline.layers.every((layer) => layer.durationSec > 0),
    withinDuration: timeline.layers.every((layer) => layer.startSec + layer.durationSec <= timeline.durationSec + 0.01),
    monotonicStarts: sorted.every((layer, index) => index === 0 || layer.startSec >= sorted[index - 1].startSec),
    canvasValid: timeline.width > 0 && timeline.height > 0 && timeline.fps >= 12
  };

  if (!checks.withinDuration) warnings.push("Some layers exceed timeline duration.");
  if (!timeline.renderHints.safeZone) warnings.push("Safe-zone rendering is disabled.");
  if (!timeline.renderHints.subtitleBurnIn) warnings.push("Subtitle burn-in is disabled.");

  const passedCount = Object.values(checks).filter(Boolean).length;
  const score = Math.round((passedCount / Object.keys(checks).length) * 100);
  return { passed: score >= 85, score, checks, warnings };
}
