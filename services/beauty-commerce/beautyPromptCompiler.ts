import type { BeautyCommerceRequest, BeautyCommerceDecision } from "./beautyCommerceTypes";

export function compileBeautyCommercePrompt(req: BeautyCommerceRequest, partial: Omit<BeautyCommerceDecision, "prompt" | "negativePrompt">) {
  const prompt = `
AI Beauty Commerce Campaign Visual.

Brand: ${req.brandName}
Product: ${req.productName ?? "brand/fashion visual"}
Product type: ${req.productType ?? "not specified"}
Industry: ${req.industry}
Audience: ${req.targetAudience}
Channel: ${req.channel}
Goal: ${req.campaignGoal}

Avatar / model:
${req.avatarDescription}

Fashion styling:
${req.outfitStyle}

Attention Routing:
${JSON.stringify(partial.attentionRouting, null, 2)}

Femininity Perception:
${JSON.stringify(partial.femininityPerception, null, 2)}

Pose Psychology:
${JSON.stringify(partial.posePsychology, null, 2)}

Eye Contact:
${JSON.stringify(partial.eyeContact, null, 2)}

Fashion Silhouette:
${JSON.stringify(partial.fashionSilhouette, null, 2)}

Soft Sensual Commercial Logic:
${JSON.stringify(partial.softSensualCommercialLogic, null, 2)}

Commercial visual direction:
Create a tasteful, premium, fashion-commercial beauty visual.
Use realistic skin texture, natural body proportions, premium lighting, clean composition, clear product/brand purpose, and platform-safe framing.
Do not over-focus on intimate body parts; the image must feel like a luxury campaign, beauty commerce ad, lookbook, or KOL product creative.
`.trim();

  const negativePrompt = [
    "explicit nudity",
    "sexual act",
    "fetish framing",
    "voyeuristic angle",
    "unrealistic anatomy",
    "over-inflated proportions",
    "plastic skin",
    "bad hands",
    "distorted product",
    "unreadable text",
    "watermark",
    "low quality",
    "off-brand styling"
  ].join(", ");

  return {prompt, negativePrompt};
}
