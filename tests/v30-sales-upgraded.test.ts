import { runStoryboardAgentV30SalesUpgraded } from "../lib/storyboard-v30/storyboardAgentRuntime.sales-upgraded";

const result = runStoryboardAgentV30SalesUpgraded({
  title: "London Fashion Week × Luxury Lipstick Launch",
  format: "fashion_runway",
  totalShots: 160,
  targetDurationSec: 240,
  requestedPhases: ["setup", "backstage", "runway", "after_party"],
  mainCharacter: "1 cô gái",
  location: "London Fashion Week",
  aspectRatio: "9:16",
  outputDir: "storage/test-v30-sales-upgraded",
  providers: { still: "hidream", video: "veo", motionAlt: "runway" },
  salesEngine: {
    enabled: true,
    productName: "son môi đỏ luxury Dior/YSL",
    category: "lipstick",
    brief: "Micro contrast on lips + lipstick only, eye highlight boost nhẹ, skin matte, lipstick touching lips",
    duration: 15,
    platform: "shorts",
    aspectRatio: "9:16",
    language: "vi",
    preserveIdentity: true,
    preserveProductShape: true,
    goal: "sale"
  }
});

const shots = result.phases.flatMap((p: any) => p.shots);
if (result.status !== "ready") throw new Error(`Expected ready, got ${result.status}`);
if (!result.salesEngineV3) throw new Error("salesEngineV3 missing");
if (!(result.verification as any).salesEngineV3?.passed) throw new Error("sales verification failed");
if (!shots.some((s: any) => s.id >= 9000)) throw new Error("sales shots were not injected");
if (!(result.providerPayloads as any).renderQueueSales?.length) throw new Error("sales render queue missing");
if ((result.salesEngineV3 as any).score.finalScore < 80) throw new Error("sales score too low");

console.log("V30 Sales Upgraded test passed:", {
  status: result.status,
  shots: shots.length,
  salesScore: (result.salesEngineV3 as any).score.finalScore
});
