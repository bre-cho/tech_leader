import type { BeautyCommerceRequest } from "./beautyCommerceTypes";

export function buildPosePsychology(req: BeautyCommerceRequest) {
  const poseMap = {
    confidence: {
      posture: "shoulders relaxed, posture upright, slight torso angle",
      perception: "confidence, premium self-assurance",
      camera: "85mm portrait, eye-level or slight low angle"
    },
    soft_feminine: {
      posture: "gentle torso turn, relaxed hands, soft smile",
      perception: "softness, approachability, feminine warmth",
      camera: "85mm soft portrait, shallow depth"
    },
    editorial: {
      posture: "asymmetric pose, controlled chin angle, fashion hand placement",
      perception: "editorial confidence and luxury distance",
      camera: "70-100mm editorial framing"
    },
    product_demo: {
      posture: "hands naturally hold product, eyes follow product movement",
      perception: "product trust and guided attention",
      camera: "close-up to medium shot, product-face alignment"
    },
    wedding_emotion: {
      posture: "graceful neck line, gentle hand movement, romantic smile",
      perception: "bridal emotion and elegance",
      camera: "soft cinematic portrait"
    },
    spa_trust: {
      posture: "relaxed shoulders, calm eye contact, caring expression",
      perception: "wellness trust and calm",
      camera: "soft frontal beauty shot"
    }
  } as const;

  return {
    ...poseMap[req.poseGoal],
    hardRules: [
      "natural body proportions",
      "no over-inflated anatomy",
      "no unrealistic pose",
      "hands must look natural",
      "pose must support commercial story"
    ]
  };
}
