import { runIdentityBeautyRuntime } from "../lib/beauty-identity-v29/identityBeautyRuntime";

const result = runIdentityBeautyRuntime({
  brandName: "Demo",
  campaignName: "test",
  visualIntent: "luxury_lipstick_ad",
  platform: "poster",
  references: [
    { id: "face", kind: "face", uri: "/face.png", lockStrength: 0.96 },
    { id: "makeup", kind: "makeup", uri: "/makeup.png" }
  ],
  faceLock: { enabled: true, strictness: 0.96 },
  output: { aspectRatio: "4:5", quality: "8K", outputDir: "storage/test-v29-1" },
  saveWinnerDna: false
});

if (result.status !== "ready") throw new Error("Runtime should be ready");
if (result.qaReport.score < 90) throw new Error("QA score too low");
if (!String((result.promptPack.data as any).prompt).includes("FACE LOCK PRIORITY")) throw new Error("Face lock prompt missing");
if (!String((result.promptPack.data as any).negativePrompt).includes("identity drift")) throw new Error("Negative prompt missing identity drift");
if (!(result.providerPayloads as any).stillImage.endpoint) throw new Error("Provider endpoint missing");

console.log("V29.1 Identity Lock Beauty Runtime test passed:", result.qaReport.score);
