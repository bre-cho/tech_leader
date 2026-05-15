import type { FaceObservation, EngineSignal } from "./facialAesthetic.types";
import { includesAny, scoreByTraits } from "./utils";

export function evaluateBeautySymmetry(observation: FaceObservation = {}): EngineSignal {
  const text = [observation.faceShape, observation.eyes, observation.notes].join(" ");

  const score = scoreByTraits(
    86,
    [
      [includesAny(text, ["balanced", "aligned", "harmony", "natural asymmetry"]), 7]
    ],
    [
      [includesAny(text, ["too symmetric", "mirror face", "doll", "uncanny"]), 16],
      [includesAny(text, ["misaligned", "distorted", "cross eye"]), 20]
    ]
  );

  return {
    id: "beauty_symmetry",
    label: "Beauty Symmetry",
    score,
    evidence: ["Commercial beauty cần harmony, không cần symmetry tuyệt đối."],
    recommendation: "Maintain balanced facial alignment with subtle natural asymmetry for realism."
  };
}
