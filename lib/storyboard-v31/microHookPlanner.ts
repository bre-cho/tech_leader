import type { RhythmNode, ShotSpec } from "./types";

const HOOKS = ["face close-up", "eye contact", "accessory macro", "flash camera", "crowd reaction", "light change", "motion beat"];

export function planMicroHooks(shots: ShotSpec[], graph: RhythmNode[]) {
  const injections: Array<{ afterShotId: number; hook: string; reason: string }> = [];
  let lastStrongHookIndex = -1;

  graph.forEach((node, idx) => {
    const strong = node.facePriority >= 9 || node.motion >= 8 || node.socialProof >= 9 || node.payoff >= 9 || node.intimacy >= 9;
    if (strong) lastStrongHookIndex = idx;

    if (idx > 0 && idx - lastStrongHookIndex >= 2) {
      const hook = HOOKS[idx % HOOKS.length];
      injections.push({
        afterShotId: shots[idx].id,
        hook,
        reason: "Cứ 2-3 shots cần attention reset cho Shorts/Reels/TikTok."
      });
      lastStrongHookIndex = idx;
    }
  });

  return {
    name: "MicroHookPlanner",
    score: Math.max(70, 100 - injections.length * 5),
    injections,
    rules: HOOKS,
    passed: injections.length <= Math.ceil(shots.length / 3)
  };
}
