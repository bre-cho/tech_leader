import { runBeautyCommerceEngine } from "../services/beauty-commerce/beautyCommerceEngine";

const res = runBeautyCommerceEngine({
  brandName: "Demo Beauty",
  productName: "Glow Serum",
  productType: "serum bottle",
  industry: "cosmetic_brand",
  targetAudience: "Vietnamese women 22-35",
  campaignGoal: "conversion",
  channel: "tiktok",
  avatarDescription: "realistic virtual Asian beauty KOL, natural skin texture",
  outfitStyle: "elegant luxury fashion styling",
  poseGoal: "product_demo",
  sensualityLevel: "soft",
  saveWinnerDna: false
});

if (res.status !== "ready") throw new Error("V28 should be ready");
if (!res.decision.prompt.includes("AI Beauty Commerce Campaign Visual")) throw new Error("prompt missing");
if ((res.verification as any).score < 90) throw new Error("verification failed");
if ((res.providerPayload as any).provider !== "banana") throw new Error("provider route failed");

console.log("V28 Beauty Commerce Engine test passed", res.commercialScore);
