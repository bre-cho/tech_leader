import type { BeautyPerceptionRequest, EngineResult } from "./types";

export function runHandToFacePsychologyEngine(req: BeautyPerceptionRequest): EngineResult {
  const desired = req.desiredSignals.join(" ").toLowerCase();
  const gestures = [
    { id: "finger_near_lips", perception: "intimacy cue", score: desired.includes("finger") || desired.includes("lips") ? 96 : 88 },
    { id: "cheek_touch", perception: "softness and approachability", score: desired.includes("cheek") ? 94 : 88 },
    { id: "chin_support", perception: "contemplative beauty", score: desired.includes("chin") ? 92 : 86 },
    { id: "collarbone_frame", perception: "elegance and fashion framing", score: desired.includes("collarbone") ? 95 : 87 },
    { id: "hair_touch", perception: "natural feminine motion", score: desired.includes("hair") ? 94 : 88 },
    { id: "shoulder_touch", perception: "soft fashion intimacy", score: desired.includes("shoulder") ? 93 : 86 },
    { id: "product_presenting", perception: "commercial conversion", score: req.productName ? 95 : 82 }
  ];

  const route = gestures
    .sort((a, b) => b.score - a.score)
    .slice(0, 4)
    .map(g => g.id);

  return {
    name: "HandToFacePsychologyEngine",
    score: Math.round(gestures.reduce((a, b) => a + b.score, 0) / gestures.length),
    data: {
      gesture_graph: gestures,
      recommended_gestures: route,
      rules: [
        "gesture must be natural, not random",
        "hands must have correct anatomy",
        "gesture should route attention toward eyes, lips, product or fashion detail",
        "avoid fetish/voyeuristic framing"
      ]
    },
    warnings: []
  };
}
