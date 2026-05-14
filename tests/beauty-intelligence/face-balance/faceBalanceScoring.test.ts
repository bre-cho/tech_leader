import { enhancePromptWithFaceWidthLock, scoreFaceBalancePrompt } from "../../../lib/beauty-intelligence/face-balance";

// Test 1: adds anti-pointed-chin prompt terms
const result = enhancePromptWithFaceWidthLock({
  basePrompt: "adult virtual Korean beauty influencer, soft compact oval face shape",
  negativePrompt: "",
  provider: "flux",
  strictGate: true
});

if (!result.prompt.includes("soft rounded compact face")) {
  throw new Error("Prompt missing: soft rounded compact face");
}
if (!result.prompt.includes("natural chin base width retention")) {
  throw new Error("Prompt missing: natural chin base width retention");
}
if (!result.prompt.includes("soft lower-face width continuity")) {
  throw new Error("Prompt missing: soft lower-face width continuity");
}
if (!result.prompt.includes("rounded blunt chin")) {
  throw new Error("Prompt missing: rounded blunt chin");
}
if (!result.negativePrompt.includes("sharp chin tip")) {
  throw new Error("Negative prompt missing: sharp chin tip");
}
if (!result.negativePrompt.includes("pinched chin base")) {
  throw new Error("Negative prompt missing: pinched chin base");
}
if (result.score.total < 80) {
  throw new Error(`Score too low: ${result.score.total} (expected >= 80)`);
}
if (!result.gatePassed) {
  throw new Error("Gate should pass");
}

console.log("✅ V29 Test 1 PASSED: adds anti-pointed-chin prompt terms");
console.log(`   Score: ${result.score.total}/100 (${result.score.grade})`);

// Test 2: scores weak face prompt lower
const weakScore = scoreFaceBalancePrompt("beautiful Korean face, V-line", "");
if (weakScore.total >= 70) {
  throw new Error(`Weak score should be < 70, got: ${weakScore.total}`);
}

console.log("✅ V29 Test 2 PASSED: scores weak face prompt lower");
console.log(`   Score: ${weakScore.total}/100 (${weakScore.grade})`);
console.log("\n✅ All V29 Face Balance tests PASSED");
