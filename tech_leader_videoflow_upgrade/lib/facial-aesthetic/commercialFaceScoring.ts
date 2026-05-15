import type { BeautyPersona, FaceObservation, EngineSignal } from "./facialAesthetic.types";
import { includesAny, scoreByTraits } from "./utils";

export function evaluateCommercialFace(persona: BeautyPersona, observation: FaceObservation = {}): EngineSignal {
  const text = [observation.eyes, observation.pose, observation.productPlacement, observation.typography, observation.notes].join(" ");

  const score = scoreByTraits(
    82,
    [
      [includesAny(text, ["eye contact", "smile", "friendly", "warm", "trust"]), 9],
      [includesAny(text, ["product in hand", "product hero", "benefits", "cta"]), 7],
      [persona.platform === "tiktok" || persona.platform === "shopee", 3]
    ],
    [
      [includesAny(text, ["no product", "confusing", "clutter", "hard to read"]), 12],
      [persona.sensualityLevel > 80, 6]
    ]
  );

  return {
    id: "commercial_face",
    label: "Commercial Face Conversion",
    score,
    evidence: [
      "Face phải truyền trust trước, sau đó route mắt sang product và benefit.",
      "Friendly eye contact + product-in-hand là parasocial commerce bridge."
    ],
    recommendation: "Use warm confident smile, direct soft eye contact, visible product-in-hand, clean benefit hierarchy."
  };
}
