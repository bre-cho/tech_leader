import type { FaceObservation, EngineSignal } from "./facialAesthetic.types";
import { includesAny, scoreByTraits } from "./utils";

export function evaluateContourHighlight(observation: FaceObservation = {}): EngineSignal {
  const text = [observation.skin, observation.lighting, observation.notes].join(" ");

  const score = scoreByTraits(
    83,
    [
      [includesAny(text, ["cheek glow", "nose highlight", "soft shadow", "premium glow", "semi-matte"]), 10],
      [includesAny(text, ["high-key", "diffuse", "catchlight", "beauty lighting"]), 5]
    ],
    [
      [includesAny(text, ["harsh contour", "overexposed", "plastic skin", "oily", "flat light"]), 14]
    ]
  );

  return {
    id: "contour_highlight",
    label: "Contour & Highlight Reasoning",
    score,
    evidence: [
      "Highlight zones: trán, sống mũi, gò má, cằm.",
      "Contour zones: mũi, cheek depth, thái dương, jaw separation."
    ],
    recommendation:
      "Add soft luxury contour, premium glow on cheekbones/nose bridge/chin, visible micro skin texture, avoid oily over-glow."
  };
}
