import type { BeautyCommerceRequest } from "./beautyCommerceTypes";

export function buildFashionSilhouette(req: BeautyCommerceRequest) {
  const style = req.outfitStyle.toLowerCase();
  const fabric =
    /silk|satin|lụa/.test(style) ? "silk/satin flow, soft highlights" :
    /lace|ren/.test(style) ? "lace texture, delicate edge detail, non-explicit fashion styling" :
    /cotton|t-shirt|áo phông/.test(style) ? "cotton tension, natural folds" :
    "premium fabric realism";

  return {
    silhouetteGoal: req.industry.includes("fashion") ? "editorial body line and garment focus" : "beauty-commercial body balance",
    fabricPhysics: [
      fabric,
      "realistic gravity",
      "natural fold tension",
      "compression zones must be subtle and realistic"
    ],
    cameraRules: [
      "85mm lens for natural proportions",
      "avoid wide-angle distortion",
      "slight torso twist for natural silhouette",
      "shoulder-back posture only if it stays realistic"
    ],
    safetyRules: [
      "adult fashion model only",
      "no explicit nudity",
      "no fetishized framing",
      "no focus on intimate body parts over commercial/product purpose"
    ]
  };
}
