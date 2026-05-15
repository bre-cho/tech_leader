import type { BeautyCommerceInput, EngineReport } from "./types";

export function runEyeContactEngine(input: BeautyCommerceInput): EngineReport {
  const product = Boolean(input.productName);
  const sequence = product
    ? [
        { beat: 1, gaze: "direct camera", reason: "trust and first-frame human connection" },
        { beat: 2, gaze: "glance to product", reason: "route attention to commercial object" },
        { beat: 3, gaze: "soft smile to camera", reason: "confirm confidence and friendliness" },
        { beat: 4, gaze: "alternate product/camera", reason: "maintain presenter realism" }
      ]
    : [
        { beat: 1, gaze: "direct warm camera gaze", reason: "trust and social intimacy" },
        { beat: 2, gaze: "slight side glance", reason: "avoid static AI stare" },
        { beat: 3, gaze: "return with micro smile", reason: "friendly commercial appeal" }
      ];

  return {
    name: "EyeContactEngine",
    score: 94,
    data: {
      sequence,
      perception: {
        "eyes looking camera": "trust",
        "eyes glancing product": "attention routing",
        "eyes returning to viewer": "conversion confidence"
      }
    },
    warnings: []
  };
}
