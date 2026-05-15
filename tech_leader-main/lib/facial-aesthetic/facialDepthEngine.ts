import type { FaceObservation, EngineSignal } from "./facialAesthetic.types";
import { includesAny, scoreByTraits } from "./utils";

export function evaluateFacialDepth(observation: FaceObservation = {}): EngineSignal {
  const text = [observation.lighting, observation.skin, observation.pose, observation.notes].join(" ");

  const score = scoreByTraits(
    80,
    [
      [includesAny(text, ["3d", "depth", "jaw separation", "cheek depth", "soft shadow"]), 12],
      [includesAny(text, ["85mm", "shallow depth", "cinematic", "editorial"]), 5]
    ],
    [
      [includesAny(text, ["flat", "washed out", "no shadow", "over-smoothed"]), 13]
    ]
  );

  return {
    id: "facial_depth",
    label: "Facial Depth",
    score,
    evidence: [
      "3D facial perception giúp ảnh beauty nhìn đắt hơn.",
      "Depth đến từ soft contour, cheek glow, jaw separation và catchlight."
    ],
    recommendation:
      "Use soft dimensional lighting, subtle cheekbone shadow, luminous but realistic skin, natural jaw separation."
  };
}
