import type { RhythmNode } from "./types";

export function validateEnergyCurve(graph: RhythmNode[]) {
  const spikes: Array<{ from: number; to: number; diff: number }> = [];
  const highRuns: Array<{ startShot: number; endShot: number; length: number }> = [];
  let runStart = -1;

  for (let i = 1; i < graph.length; i++) {
    const diff = Math.abs(graph[i].energy - graph[i - 1].energy);
    if (diff > 6) spikes.push({ from: graph[i - 1].shotId, to: graph[i].shotId, diff });

    if (graph[i].energy >= 8 && graph[i - 1].energy >= 8) {
      if (runStart === -1) runStart = i - 1;
    } else if (runStart !== -1) {
      const length = i - runStart;
      if (length >= 5) highRuns.push({ startShot: graph[runStart].shotId, endShot: graph[i - 1].shotId, length });
      runStart = -1;
    }
  }

  if (runStart !== -1) {
    const length = graph.length - runStart;
    if (length >= 5) highRuns.push({ startShot: graph[runStart].shotId, endShot: graph[graph.length - 1].shotId, length });
  }

  const avgEnergy = Number((graph.reduce((a, b) => a + b.energy, 0) / Math.max(1, graph.length)).toFixed(2));
  const passed = spikes.length < 5 && highRuns.length === 0;

  return {
    name: "EnergyCurveValidator",
    passed,
    score: Math.max(0, 100 - spikes.length * 8 - highRuns.length * 15),
    avgEnergy,
    spikes,
    highRuns,
    rule: "Shorts mạnh đi theo LOW → MID → HIGH → RELEASE, không HIGH liên tục gây viewer fatigue."
  };
}
