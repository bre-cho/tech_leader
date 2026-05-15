import type { RhythmNode } from "./types";

export function validateFaceRetentionPriority(graph: RhythmNode[]) {
  const gaps: Array<{ fromShot: number; toShot: number; gap: number }> = [];
  let lastFaceIdx = -1;

  graph.forEach((node, idx) => {
    if (node.facePriority >= 9) lastFaceIdx = idx;
    if (idx > 0 && idx - lastFaceIdx > 5) {
      gaps.push({
        fromShot: graph[Math.max(0, lastFaceIdx)].shotId,
        toShot: node.shotId,
        gap: idx - lastFaceIdx
      });
      lastFaceIdx = idx;
    }
  });

  return {
    name: "FaceRetentionPriority",
    passed: gaps.length === 0,
    score: Math.max(0, 100 - gaps.length * 12),
    gaps,
    rule: "Every 4-6 shots should contain face close-up or eye contact because EYES + FACE + MICRO EXPRESSION retain viewers."
  };
}
