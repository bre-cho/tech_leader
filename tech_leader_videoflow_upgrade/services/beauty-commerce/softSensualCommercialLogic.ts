import type { BeautyCommerceRequest } from "./beautyCommerceTypes";

export function buildSoftSensualCommercialLogic(req: BeautyCommerceRequest) {
  const level = req.sensualityLevel;
  const base = {
    allowedFrame: "tasteful fashion/editorial beauty, commercial-safe",
    disallowedFrame: [
      "explicit nudity",
      "sexual act implication",
      "fetish styling",
      "voyeuristic angle",
      "overly anatomical body focus"
    ],
    commercialPurpose: req.productName ? "support product desire and beauty trust" : "support fashion aspiration and brand memory"
  };

  if (level === "none") {
    return {...base, tone: "clean beauty / premium fashion", styling: "modest, elegant, brand-safe"};
  }
  if (level === "fashion_editorial") {
    return {...base, tone: "editorial glamour, confident and sophisticated", styling: "luxury fashion styling with tasteful body line"};
  }
  return {...base, tone: "soft sensual but non-explicit commercial elegance", styling: "subtle confidence, soft lighting, premium beauty posture"};
}
