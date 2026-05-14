import type { BeautyIdentityRuntimeRequest, RuntimeReport } from "./types";

export function extractBeautyIdentityDna(req: BeautyIdentityRuntimeRequest): RuntimeReport {
  const faceRefs = req.references.filter(r => r.kind === "face");
  const makeupRefs = req.references.filter(r => r.kind === "makeup");
  const hairRefs = req.references.filter(r => r.kind === "hair");

  const dna = {
    face_structure: [
      "soft oval Asian facial structure",
      "large almond-shaped eyes with strong catchlight retention",
      "natural aegyo-sal under-eye softness",
      "small refined nose bridge",
      "soft feminine jawline",
      "small V-shape chin structure",
      "natural asymmetry preserved"
    ],
    skin: [
      "high realism skin texture",
      "visible natural pores",
      "soft warm pink undertone",
      "subtle cheek blush diffusion",
      "no AI plastic smoothing"
    ],
    makeup: [
      "dewy glass skin finish",
      "gradient soft pink/coral lips",
      "natural glossy lip hydration",
      "minimal eyeliner",
      "long separated lashes",
      "soft peach-pink blush",
      "natural eyebrow texture"
    ],
    hair: [
      "dark soft hair with natural shine",
      "face framing strands",
      "consistent hair parting from reference where applicable",
      "realistic hair strand detail"
    ],
    reference_coverage: {
      face: faceRefs.length,
      makeup: makeupRefs.length,
      hair: hairRefs.length,
      total: req.references.length
    }
  };

  const score = Math.min(98, 86 + faceRefs.length * 6 + makeupRefs.length * 3 + hairRefs.length * 2);

  return {
    name: "BeautyIdentityDnaExtractor",
    score,
    data: dna,
    warnings: faceRefs.length === 0 ? ["No face reference supplied. Strict identity lock will rely on textual DNA only."] : []
  };
}
