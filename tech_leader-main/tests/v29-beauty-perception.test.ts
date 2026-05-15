import { runBeautyPerceptionGraphEngine } from "../lib/beauty-perception-v29/beautyPerceptionGraphEngine";

const result = runBeautyPerceptionGraphEngine({
  brandName: "Demo Beauty",
  campaignName: "test_campaign",
  productName: "Glow Serum",
  platform: "tiktok",
  lightingStyle: "KOREAN_SOFT",
  identityDna: {
    faceGeometry: "soft oval balanced face",
    eyeRatio: "large bright almond eyes",
    lipRatio: "natural lips",
    noseSoftness: "soft refined nose",
    eyebrowCurvature: "straight eyebrows",
    skinTone: "light neutral-warm Asian skin",
    moleMap: "tiny cheek mole",
    aegyoSal: "soft aegyo-sal",
    jawSoftness: "soft feminine jaw",
    hairTexture: "long dark hair",
    smileSignature: "micro warm smile"
  },
  desiredSignals: ["direct eye contact", "slight smile", "finger near lips", "collarbone elegance", "shallow DOF"],
  references: [
    { kind: "identity_ref", label: "identity", uri: "/a.png" },
    { kind: "makeup_ref", label: "makeup", uri: "/b.png" },
    { kind: "lighting_ref", label: "lighting", uri: "/c.png" }
  ],
  sceneCount: 5,
  saveMemory: false
});

if (result.status !== "ready") throw new Error("V29 should be ready");
if ((result.commercialBeautyScore as any).beauty_score < 90) throw new Error("beauty score too low");
if (!String((result.promptPack as any).prompt).includes("Beauty is not a pretty face")) throw new Error("core prompt missing");
if (result.graph.nodes.length < 15) throw new Error("graph nodes missing");
if (!(result.socialCtrPrediction as any).data.estimated_ctr_range) throw new Error("CTR prediction missing");

console.log("V29 Beauty Perception Graph Engine test passed:", result.commercialBeautyScore);
