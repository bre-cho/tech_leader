import type { StoryboardRequest, PhasePlan } from "./types";

export function runContinuityEngine(req: StoryboardRequest, phases: PhasePlan[]) {
  const shots = phases.flatMap(p => p.shots);
  const checks = {
    has_setup: phases.some(p => p.phase === "setup"),
    has_backstage: phases.some(p => p.phase === "backstage"),
    has_runway: phases.some(p => p.phase === "runway"),
    has_after_party: phases.some(p => p.phase === "after_party"),
    all_shots_have_prompt: shots.every(s => s.prompt.length > 50),
    all_shots_have_provider_payload: shots.every(s => Boolean(s.providerPayload?.endpoint)),
    face_lock_in_prompts: req.identityDna.faceLock ? shots.every(s => s.prompt.includes("same female model face identity")) : true,
    continuity_tags_present: shots.every(s => s.continuityTags.length >= 4),
    duration_total_positive: shots.reduce((a, s) => a + s.durationSec, 0) > 0
  };

  const score = Math.round(Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 100);

  return {
    name: "StoryboardContinuityEngine",
    score,
    passed: score >= 90,
    checks,
    continuityContracts: {
      protagonist: req.identityDna.characterNotes,
      location: req.location,
      aspectRatio: req.aspectRatio,
      phaseOrder: req.requestedPhases,
      wardrobe: req.identityDna.wardrobeContinuity ? "locked per phase" : "flexible",
      hairMakeup: req.identityDna.hairMakeupContinuity ? "locked per phase" : "flexible"
    },
    issues: Object.entries(checks).filter(([, v]) => !v).map(([k]) => k)
  };
}
