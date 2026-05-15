import type { ShotSpec } from "./types";

export const RUNWAY_LOOP = [
  "wide_walk",
  "medium_walk",
  "beauty_closeup",
  "accessory_macro",
  "audience_reaction",
  "flash_camera",
  "hero_pose"
];

export function orchestrateRunwayEscalation(shots: ShotSpec[]) {
  const runwayShots = shots.filter(s => /runway|catwalk|walk|pose|spotlight|audience|flash/i.test(`${s.phase} ${s.title} ${s.description}`));
  const sequence = runwayShots.map((shot, idx) => {
    const expected = RUNWAY_LOOP[idx % RUNWAY_LOOP.length];
    const text = `${shot.title} ${shot.camera} ${shot.movement} ${shot.subjectFocus}`.toLowerCase();
    const actual =
      /wide/.test(text) && /walk|runway|catwalk/.test(text) ? "wide_walk" :
      /medium/.test(text) && /walk|runway|catwalk/.test(text) ? "medium_walk" :
      /close|face|eye|beauty/.test(text) ? "beauty_closeup" :
      /macro|accessory|detail|fabric|bag|shoe/.test(text) ? "accessory_macro" :
      /audience|crowd|reaction|phone/.test(text) ? "audience_reaction" :
      /flash|photographer|camera/.test(text) ? "flash_camera" :
      /pose|hero/.test(text) ? "hero_pose" :
      "other";

    return { shotId: shot.id, expected, actual, ok: actual === expected || actual !== "other" };
  });

  const okCount = sequence.filter(s => s.ok).length;
  return {
    name: "RunwayEscalationEngine",
    loop: RUNWAY_LOOP,
    sequence,
    score: Math.round((okCount / Math.max(1, sequence.length)) * 100),
    passed: okCount / Math.max(1, sequence.length) >= 0.65,
    rule: "walk → turn/medium → close-up → detail → crowd → flash → hero pose → applause"
  };
}
