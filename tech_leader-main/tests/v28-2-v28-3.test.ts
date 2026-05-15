import { runBeautyCommerceV28 } from "../lib/beauty-commerce-v28/beautyCommerceV28Engine";

const result = runBeautyCommerceV28({
  brandName: "Demo Beauty",
  productName: "Glow Serum",
  productType: "serum bottle",
  industry: "tiktok_beauty_ads",
  avatarDna: "realistic Vietnamese/Asian beauty KOL, natural skin texture, soft feminine commercial look",
  campaignGoal: "conversion",
  channel: "tiktok",
  sceneCount: 5,
  durationSec: 15,
  references: [
    { kind: "identity", label: "face", uri: "/x.png" },
    { kind: "makeup", label: "makeup", uri: "/m.png" },
    { kind: "lighting", label: "lighting", uri: "/l.png" }
  ],
  saveWinnerDna: false
});

if (result.status !== "ready") throw new Error("engine should be ready");
if ((result.commercialScore as any).final_score < 90) throw new Error("commercial score too low");
if (!result.prompt.includes("Commercial Beauty Psychology")) throw new Error("prompt compiler missing commercial psychology");
if (!(result.videoPlan as any).scenes || (result.videoPlan as any).scenes.length !== 5) throw new Error("video plan scenes failed");
if ((result.providerRoute as any).imageProvider !== "banana") throw new Error("banana should be routed as image provider");

console.log("V28.2/V28.3 test passed:", result.commercialScore);
