import type { FacialAestheticOutput } from "./types";

export function verifyFacialAesthetic(output: Omit<FacialAestheticOutput, "verification">) {
  const checks = {
    face_dna_exists: Boolean(output.face_dna),
    facial_balance_defined: Boolean(output.facial_balance.face_shape),
    nose_mapping_defined: Object.keys(output.nose_structure.perception_mapping).length >= 4,
    contour_highlight_defined: output.contour_highlight.highlight_zones.length >= 4,
    facial_depth_defined: output.facial_depth.depth_cues.length >= 4,
    beauty_symmetry_defined: output.beauty_symmetry.natural_asymmetry_rules.length >= 3,
    scoring_passed: output.luxury_face_scoring.passed,
    prompt_enhancer_exists: output.prompt_enhancer.includes("FACIAL AESTHETIC PERCEPTION ENGINE"),
    negative_prompt_blocks_ai_doll: output.negative_prompt.includes("AI doll face")
  };

  const score = Math.round(Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 100);

  return {
    passed: score >= 90,
    score,
    checks,
    issues: Object.entries(checks).filter(([, v]) => !v).map(([k]) => k)
  };
}
