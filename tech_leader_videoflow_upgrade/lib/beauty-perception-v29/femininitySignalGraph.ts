import type { BeautyPerceptionRequest, EngineResult, GraphNode, GraphEdge } from "./types";

export function buildFemininitySignalGraph(req: BeautyPerceptionRequest): EngineResult<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
  const signals = [
    ["shoulder_angle", "soft shoulder angle", "femininity"],
    ["neck_exposure", "neck exposure", "elegance"],
    ["collarbone_visibility", "collarbone visibility", "luxury elegance"],
    ["waist_perception", "waist perception", "silhouette attractiveness"],
    ["hand_softness", "hand softness", "intimacy"],
    ["posture_softness", "posture softness", "approachability"],
    ["facial_softness", "facial softness", "trust"],
    ["eye_openness", "eye openness", "attention lock"],
    ["smile_warmth", "smile warmth", "friendliness"],
    ["movement_elegance", "movement elegance", "video realism"]
  ];

  const desired = req.desiredSignals.join(" ").toLowerCase();
  const nodes = signals.map(([id, label, perception]) => ({
    id,
    type: "FemininitySignal",
    label,
    score: desired.includes(label.split(" ")[0]) || desired.includes(String(perception).split(" ")[0]) ? 95 : 88,
    properties: { perception }
  }));

  const edges: GraphEdge[] = [
    { from: "shoulder_angle", to: "femininity", relation: "drives", weight: 0.84, reasoning: "soft shoulder angle creates feminine softness" },
    { from: "collarbone_visibility", to: "elegance", relation: "drives", weight: 0.78, reasoning: "collarbone highlight creates elegance without explicit framing" },
    { from: "hand_softness", to: "intimacy", relation: "drives", weight: 0.82, reasoning: "soft hand placement increases closeness and warmth" },
    { from: "eye_openness", to: "attention_lock", relation: "drives", weight: 0.9, reasoning: "open direct eyes lock viewer attention" },
    { from: "movement_elegance", to: "realism", relation: "supports", weight: 0.76, reasoning: "tiny motion prevents mannequin effect" }
  ];

  return {
    name: "FemininitySignalGraph",
    score: Math.round(nodes.reduce((a, b) => a + (b.score ?? 0), 0) / nodes.length),
    data: { nodes, edges },
    warnings: []
  };
}
