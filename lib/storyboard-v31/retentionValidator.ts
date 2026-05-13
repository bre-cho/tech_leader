import type { RhythmNode, ShotSpec } from "./types";

export function validateRetention(shots: ShotSpec[], graph: RhythmNode[], timeline: any, durationSec: number) {
  let elapsed = 0;
  const timed = shots.map((s, idx) => {
    const start = elapsed;
    elapsed += s.durationSec;
    return { shot: s, rhythm: graph[idx], start, end: elapsed };
  });

  const beatChecks = timeline.beats.map((beat: any) => {
    const contained = timed.filter(t => t.start < beat.endSec && t.end > beat.startSec);
    const avgEnergy = contained.length ? contained.reduce((a, b) => a + b.rhythm.energy, 0) / contained.length : 0;
    const hasFace = contained.some(t => t.rhythm.facePriority >= 9);
    const hasMotion = contained.some(t => t.rhythm.motion >= 8);
    const hasSocial = contained.some(t => t.rhythm.socialProof >= 9);
    const hasPayoff = contained.some(t => t.rhythm.payoff >= 9);
    const ok =
      /beauty|face/i.test(beat.role + beat.requiredHook) ? hasFace :
      /motion|runway|climax|spectacle/i.test(beat.role + beat.requiredHook) ? hasMotion || hasSocial || hasPayoff :
      /release|ending/i.test(beat.role) ? hasPayoff || avgEnergy <= 7 :
      avgEnergy >= Math.max(5, beat.targetEnergy - 3);

    return { ...beat, shots: contained.map(t => t.shot.id), avgEnergy: Number(avgEnergy.toFixed(2)), hasFace, hasMotion, hasSocial, hasPayoff, ok };
  });

  const passedCount = beatChecks.filter((b: any) => b.ok).length;
  return {
    name: "RetentionValidator",
    passed: passedCount / Math.max(1, beatChecks.length) >= 0.75,
    score: Math.round((passedCount / Math.max(1, beatChecks.length)) * 100),
    beatChecks,
    totalDurationSec: Number(elapsed.toFixed(2)),
    targetDurationSec: durationSec
  };
}
