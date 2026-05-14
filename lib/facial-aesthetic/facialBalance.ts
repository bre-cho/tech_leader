import type { BeautyPersona, FaceObservation, EngineSignal } from "./facialAesthetic.types";
import { includesAny, scoreByTraits } from "./utils";

export function evaluateFacialBalance(persona: BeautyPersona, observation: FaceObservation = {}): EngineSignal {
  const text = [observation.faceShape, observation.jawline, observation.eyes, observation.lips, observation.notes].join(" ");
  const score = scoreByTraits(
    84,
    [
      [includesAny(text, ["oval", "balanced", "harmony", "symmetry", "soft"]), 8],
      [includesAny(text, ["natural", "realistic", "commercial"]), 5],
      [persona.realismLevel >= 85, 3]
    ],
    [
      [includesAny(text, ["doll", "plastic", "over perfect", "too symmetric", "sharp chin"]), 14],
      [persona.sensualityLevel > 75 && persona.softnessLevel < 70, 6]
    ]
  );

  return {
    id: "facial_balance",
    label: "Facial Balance",
    score,
    evidence: [
      "Ưu tiên mặt oval mềm, cân bằng mắt-mũi-miệng, jawline tự nhiên.",
      "Chặn cảm giác AI doll/perfect symmetry giả."
    ],
    recommendation:
      score >= 90
        ? "Giữ cấu trúc gương mặt hiện tại, chỉ tinh chỉnh highlight-shadow nhẹ."
        : "Tăng soft oval face, natural asymmetry, jawline mềm và micro texture để tạo commercial realism."
  };
}
