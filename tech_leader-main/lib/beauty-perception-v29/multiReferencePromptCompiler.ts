import type { BeautyPerceptionRequest, EngineResult } from "./types";

const REQUIRED = ["identity_ref", "makeup_ref", "fashion_ref", "lighting_ref", "pose_ref", "gesture_ref", "hair_ref", "skin_ref"] as const;

export function compileMultiReferenceSceneSpec(req: BeautyPerceptionRequest, engines: Record<string, EngineResult>): EngineResult {
  const locks = REQUIRED.map(kind => {
    const refs = req.references.filter(r => r.kind === kind);
    return {
      kind,
      available: refs.length > 0,
      labels: refs.map(r => r.label),
      lock_strength: refs.length ? Math.max(...refs.map(r => r.lockStrength)) : 0
    };
  });

  const sceneSpec = {
    identity_lock: true,
    eye_contact: "direct_soft",
    smile: "micro_warm",
    lighting: req.lightingStyle,
    pose: req.desiredSignals.some(s => /head tilt/i.test(s)) ? "head_tilt_left" : "soft_portrait_pose",
    gesture: req.desiredSignals.some(s => /finger|lips/i.test(s)) ? "finger_near_lips" : "cheek_touch_or_soft_hand_frame",
    lens: "85mm_f1_8",
    skin: "real_pores_visible",
    background: req.lightingStyle === "DARK_EDITORIAL" ? "pitch_black_spotlight" : "minimal_soft_bokeh",
    reference_locks: locks,
    commercial_goal: req.productName ? "face_to_product_conversion" : "parasocial_beauty_trust"
  };

  const prompt = `
Commercial Beauty Scene Spec:
${JSON.stringify(sceneSpec, null, 2)}

Reference conditioning:
${locks.map(l => `- ${l.kind}: ${l.available ? l.labels.join(", ") : "missing; infer from DNA"}; lock=${l.lock_strength}`).join("\n")}

Use the Beauty Perception Graph:
- eyes → trust
- slight smile → friendliness
- head tilt → softness
- collarbone → elegance
- off-shoulder/fashion frame → femininity
- soft hair framing → face slimming perception
- warm backlight/windowlight → emotional warmth
- shallow DOF → luxury photography feel
- finger near lips/cheek touch → intimacy cue
- direct eye contact → attention lock
`.trim();

  const coverage = locks.filter(l => l.available).length / locks.length;

  return {
    name: "MultiReferencePromptCompiler",
    score: Math.round(80 + coverage * 20),
    data: { sceneSpec, prompt, reference_coverage: coverage },
    warnings: locks.filter(l => !l.available).map(l => `Missing ${l.kind}; inferred from identity DNA.`)
  };
}
