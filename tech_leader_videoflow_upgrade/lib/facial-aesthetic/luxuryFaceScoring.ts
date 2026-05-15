import type { BeautyPersona, FaceObservation, EngineSignal } from "./facialAesthetic.types";
import { includesAny, scoreByTraits } from "./utils";

export function evaluateLuxuryFace(persona: BeautyPersona, observation: FaceObservation = {}): EngineSignal {
  const text = [observation.skin, observation.makeup, observation.lighting, observation.notes].join(" ");

  const score = scoreByTraits(
    78 + persona.luxuryLevel * 0.12,
    [
      [includesAny(text, ["editorial", "premium", "luxury", "serif", "gold", "champagne"]), 8],
      [includesAny(text, ["clean makeup", "soft contour", "glow", "high-end"]), 7]
    ],
    [
      [includesAny(text, ["cheap", "overdone", "low quality", "plastic", "harsh"]), 15]
    ]
  );

  return {
    id: "luxury_face",
    label: "Luxury Beauty Perception",
    score,
    evidence: [
      "Luxury perception đến từ restraint: clean makeup, glow kiểm soát, contour mềm, typography thở."
    ],
    recommendation: "Increase editorial restraint, champagne/gold micro highlights, clean semi-matte skin, no over-retouching."
  };
}
