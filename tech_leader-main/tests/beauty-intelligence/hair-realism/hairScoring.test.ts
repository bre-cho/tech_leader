import { enhanceScenePromptWithHairRealism, scoreHairRealismPrompt } from "../../../lib/beauty-intelligence/hair-realism";

// Test 1: enhances scene prompt with required hair realism terms
const result = enhanceScenePromptWithHairRealism({
  sceneId: 1,
  basePrompt: "adult virtual Korean beauty influencer",
  provider: "flux",
  strictGate: true
});

if (!result.prompt.includes("extremely realistic individual hair strands")) {
  throw new Error("Prompt missing: extremely realistic individual hair strands");
}
if (!result.prompt.includes("visible natural hair fiber texture")) {
  throw new Error("Prompt missing: visible natural hair fiber texture");
}
if (!result.prompt.includes("natural baby hairs around forehead and cheeks")) {
  throw new Error("Prompt missing: natural baby hairs around forehead and cheeks");
}
if (!result.prompt.includes("physically accurate hair lighting")) {
  throw new Error("Prompt missing: physically accurate hair lighting");
}
if (!result.negativePrompt.includes("plastic hair")) {
  throw new Error("Negative prompt missing: plastic hair");
}
if (result.score.total < 80) {
  throw new Error(`Score too low: ${result.score.total} (expected >= 80)`);
}
if (!result.gatePassed) {
  throw new Error("Gate should pass");
}

console.log("✅ V27 Test 1 PASSED: enhances scene prompt with required hair realism terms");
console.log(`   Score: ${result.score.total}/100 (${result.score.grade})`);

// Test 2: fails weak prompt score
const weakScore = scoreHairRealismPrompt("beautiful model with nice hair", "");
if (weakScore.total >= 70) {
  throw new Error(`Weak score should be < 70, got: ${weakScore.total}`);
}
if (weakScore.grade !== "FAIL") {
  throw new Error(`Grade should be FAIL, got: ${weakScore.grade}`);
}

console.log("✅ V27 Test 2 PASSED: fails weak prompt score");
console.log(`   Score: ${weakScore.total}/100 (${weakScore.grade})`);
console.log("\n✅ All V27 Hair Realism tests PASSED");
