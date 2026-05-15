import type { BeautyPerceptionRequest, GraphNode, GraphEdge, EngineResult } from "./types";

export function buildBeautyDnaGraph(req: BeautyPerceptionRequest): EngineResult<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
  const dna = req.identityDna;
  const nodes: GraphNode[] = [
    node("face_geometry", "IdentityDNA", "Face Geometry", 94, { value: dna.faceGeometry }),
    node("eye_ratio", "IdentityDNA", "Eye Ratio", 94, { value: dna.eyeRatio }),
    node("lip_ratio", "IdentityDNA", "Lip Ratio", 90, { value: dna.lipRatio }),
    node("nose_softness", "IdentityDNA", "Nose Softness", 88, { value: dna.noseSoftness }),
    node("eyebrow_curvature", "IdentityDNA", "Eyebrow Curvature", 86, { value: dna.eyebrowCurvature }),
    node("skin_tone", "IdentityDNA", "Skin Tone", 92, { value: dna.skinTone }),
    node("mole_map", "IdentityDNA", "Mole Map", dna.moleMap ? 95 : 75, { value: dna.moleMap ?? "not provided" }),
    node("aegyo_sal", "IdentityDNA", "Aegyo-sal", 90, { value: dna.aegyoSal }),
    node("jaw_softness", "IdentityDNA", "Jaw Softness", 91, { value: dna.jawSoftness }),
    node("hair_texture", "IdentityDNA", "Hair Texture", 92, { value: dna.hairTexture }),
    node("smile_signature", "IdentityDNA", "Smile Signature", 93, { value: dna.smileSignature })
  ];

  const edges: GraphEdge[] = [
    edge("eye_ratio", "trust", "drives", 0.86, "bright eyes drive parasocial trust"),
    edge("smile_signature", "friendliness", "drives", 0.88, "micro warm smile increases approachability"),
    edge("skin_tone", "realism", "supports", 0.82, "consistent skin tone supports identity and realism"),
    edge("hair_texture", "face_slimming", "supports", 0.75, "soft hair framing can slim face perception"),
    edge("jaw_softness", "femininity", "drives", 0.8, "soft jawline supports approachable femininity")
  ];

  return {
    name: "BeautyDnaGraph",
    score: Math.round(nodes.reduce((a, b) => a + (b.score ?? 0), 0) / nodes.length),
    data: { nodes, edges },
    warnings: dna.moleMap ? [] : ["moleMap not supplied; identity lock can be improved with mole/skin detail map."]
  };
}

function node(id: string, type: string, label: string, score: number, properties: Record<string, unknown>): GraphNode {
  return { id, type, label, score, properties };
}

function edge(from: string, to: string, relation: string, weight: number, reasoning: string): GraphEdge {
  return { from, to, relation, weight, reasoning };
}
