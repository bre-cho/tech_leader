import { runStoryboardV31 } from "../lib/storyboard-v31/storyboardV31Runtime";

const result = runStoryboardV31({
  title: "Fashion Shorts Test",
  concept: "London Fashion Week cinematic runway short",
  platform: "youtube_shorts",
  targetDurationSec: 35,
  musicBpm: 118,
  outputDir: "storage/test-v31-storyboard",
  provider: { image: "hidream", video: "veo", motionFallback: "runway" }
});

if (result.status !== "ready") throw new Error(`Expected ready, got ${result.status}`);
if (result.rhythmGraph.length !== result.shots.length) throw new Error("Rhythm graph must match shot count");
const pp = result.providerPayloads as any;
const vf = result.verification as any;
if (!pp.videoShots.items.every((x: any) => x.endpoint)) throw new Error("Missing provider endpoint");
if (vf.score < 75) throw new Error("Verification score too low");
if (!pp.renderQueue || pp.renderQueue.length !== result.shots.length) throw new Error("Render queue missing");

console.log("V31 Storyboard Retention Rhythm test passed:", {
  status: result.status,
  shots: result.shots.length,
  score: result.verification.score
});
