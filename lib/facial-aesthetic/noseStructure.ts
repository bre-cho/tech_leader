import type { FaceObservation, EngineSignal } from "./facialAesthetic.types";
import { includesAny, scoreByTraits } from "./utils";

export function evaluateNoseStructure(observation: FaceObservation = {}): EngineSignal {
  const text = [observation.noseBridge, observation.noseTip, observation.notes].join(" ");

  const score = scoreByTraits(
    82,
    [
      [includesAny(text, ["high", "elegant", "refined", "natural", "soft contour"]), 10],
      [includesAny(text, ["balanced width", "slim definition", "nose bridge highlight"]), 6]
    ],
    [
      [includesAny(text, ["plastic", "surgery", "over sharp", "pinched", "fake"]), 18],
      [includesAny(text, ["flat", "wide harsh", "distorted"]), 8]
    ]
  );

  return {
    id: "nose_structure",
    label: "Nose Structure",
    score,
    evidence: [
      "Sống mũi cao tạo elegance, nhưng phải giữ natural contour.",
      "Đầu mũi refined giúp tăng luxury beauty, tránh plastic surgery look."
    ],
    recommendation:
      "Use: high elegant nose bridge, refined natural nose tip, soft nose contour, delicate bridge highlight, no plastic surgery look."
  };
}
