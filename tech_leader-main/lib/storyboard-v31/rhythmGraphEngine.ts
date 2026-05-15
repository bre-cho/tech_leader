import type { RhythmNode, ShotSpec } from "./types";

function score(text: string, patterns: Array<[RegExp, number]>, fallback: number) {
  const hit = patterns.find(([rx]) => rx.test(text));
  return hit ? hit[1] : fallback;
}

export function buildRhythmGraph(shots: ShotSpec[]): RhythmNode[] {
  return shots.map((s) => {
    const text = `${s.title} ${s.description} ${s.camera} ${s.movement} ${s.subjectFocus} ${s.emotionBeat}`.toLowerCase();

    const energy = score(text, [
      [/runway|walk|catwalk|spotlight|flash|dance|power|first step|telephoto/, 9],
      [/close|face|eye|lips|macro|beauty/, 6],
      [/rest|relax|sleep|release|breath/, 3],
      [/applause|finale|confetti|hero pose|payoff/, 8]
    ], 5);

    const intimacy = score(text, [
      [/macro|close|face|eye|lips|portrait|smile/, 9],
      [/medium|hand|accessory/, 6],
      [/wide|crowd|runway/, 3]
    ], 4);

    const motion = score(text, [
      [/tracking|orbit|slow motion|walk|catwalk|pan|dolly|push|handheld/, 8],
      [/static|hold/, 3],
      [/timelapse|flash cut/, 9]
    ], 5);

    const tension = score(text, [
      [/countdown|wait|deep breath|backstage|before|anticipation|preparation/, 8],
      [/climax|hero|spotlight/, 7],
      [/release|applause|after/, 3]
    ], 4);

    const payoff = score(text, [
      [/applause|finale|confetti|cheers|hero pose|payoff|smile/, 10],
      [/reaction|flash|crowd|phones/, 8],
      [/setup|preparation|backstage/, 3]
    ], 3);

    const facePriority = /close|face|eye|lips|portrait|smile|beauty/.test(text) ? 10 : /medium/.test(text) ? 5 : 2;
    const socialProof = /crowd|audience|phones|photographer|flash|applause|press|story|instagram/.test(text) ? 10 : 2;

    const hookType =
      facePriority >= 9 ? "face_retention" :
      socialProof >= 9 ? "social_proof" :
      motion >= 8 ? "motion" :
      payoff >= 9 ? "payoff" :
      intimacy >= 8 ? "detail" :
      "context";

    return { shotId: s.id, phase: s.phase, energy, intimacy, motion, tension, payoff, facePriority, socialProof, hookType };
  });
}
