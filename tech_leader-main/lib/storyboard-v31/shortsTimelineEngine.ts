import type { RetentionBeat, StoryboardV31Request } from "./types";

export function buildShortsRetentionGraph(req: StoryboardV31Request): { beats: RetentionBeat[]; rules: string[] } {
  const max = req.targetDurationSec;
  const raw: RetentionBeat[] = [
    { startSec: 0, endSec: 1, role: "pattern interrupt", requiredHook: "flash/light/motion", targetEnergy: 9 },
    { startSec: 1, endSec: 3, role: "beauty hook", requiredHook: "face close-up / eye contact", targetEnergy: 7 },
    { startSec: 3, endSec: 6, role: "motion escalation", requiredHook: "tracking / first step / hair motion", targetEnergy: 8 },
    { startSec: 6, endSec: 12, role: "runway climax", requiredHook: "walk / turn / crowd / flash", targetEnergy: 9 },
    { startSec: 12, endSec: 18, role: "face emotional lock", requiredHook: "micro-expression / close-up", targetEnergy: 7 },
    { startSec: 18, endSec: 25, role: "spectacle", requiredHook: "hero pose / wide / audience", targetEnergy: 9 },
    { startSec: 25, endSec: Math.max(30, max), role: "release + luxury ending", requiredHook: "applause / smile / wide outro", targetEnergy: 5 }
  ].filter(b => b.startSec < max).map(b => ({ ...b, endSec: Math.min(b.endSec, max) }));

  return {
    beats: raw,
    rules: [
      "0-1s must create pattern interrupt.",
      "1-3s must show beauty/face hook.",
      "Every 2-3 seconds must reset attention via face, motion, light, crowd, or detail.",
      "6-12s must escalate motion and runway rhythm.",
      "Last beat must release emotional tension."
    ]
  };
}
