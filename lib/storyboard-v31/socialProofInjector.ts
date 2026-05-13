import type { RhythmNode, ShotSpec } from "./types";

export function analyzeAndInjectSocialProof(shots: ShotSpec[], graph: RhythmNode[]) {
  const socialShots = graph.filter(g => g.socialProof >= 9).map(g => g.shotId);
  const needed = Math.max(1, Math.floor(shots.length / 7));
  const injections: Array<{ afterShotId: number; type: string; reason: string }> = [];

  if (socialShots.length < needed) {
    for (let i = 5; i < shots.length && injections.length < needed - socialShots.length; i += 7) {
      injections.push({
        afterShotId: shots[i].id,
        type: ["audience reaction", "photographer flash", "phone POV", "applause", "story upload"][injections.length % 5],
        reason: "Social proof tells the subconscious: THIS EVENT MATTERS."
      });
    }
  }

  return {
    name: "SocialProofInjector",
    socialShots,
    injections,
    needed,
    score: socialShots.length >= needed ? 100 : Math.max(70, 100 - injections.length * 8),
    passed: socialShots.length + injections.length >= needed
  };
}
