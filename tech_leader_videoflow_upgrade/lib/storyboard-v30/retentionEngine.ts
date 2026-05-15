import type { PhasePlan } from "./types";

export function buildRetentionPacingMap(phases: PhasePlan[]) {
  const shots = phases.flatMap(p => p.shots);
  let t = 0;
  const map = shots.map((shot, idx) => {
    const start = Number(t.toFixed(2));
    t += shot.durationSec;
    const end = Number(t.toFixed(2));
    const role =
      idx < 5 ? "opening context + curiosity" :
      shot.phase === "backstage" ? "preparation tension and beauty detail" :
      shot.phase === "runway" ? "high-fashion climax and social proof" :
      "celebration, social proof and emotional closure";

    return {
      shotId: shot.id,
      phase: shot.phase,
      start,
      end,
      role,
      retentionHook:
        /close|cận|mắt|môi|face|eye/i.test(shot.title + shot.camera) ? "beauty close-up hook" :
        /reaction|khán giả|flash|camera/i.test(shot.title) ? "social proof hook" :
        /runway|catwalk|bước|walk/i.test(shot.title) ? "motion/rhythm hook" :
        "context/detail hook"
    };
  });

  return {
    totalDurationSec: Number(t.toFixed(2)),
    pacing: map,
    rules: [
      "Alternate wide context with close-up beauty/detail shots.",
      "Use backstage tension before runway payoff.",
      "Use runway rhythm: walk → detail → reaction → face → pose.",
      "After party shifts mood to neon social proof and emotional closure."
    ]
  };
}
