import { runStoryboardV31 } from "../lib/storyboard-v31/storyboardV31Runtime";
import { compileStoryboardToVideoFlow, verifyVideoFlowTimeline } from "../lib/videoflow";

const storyboard = runStoryboardV31({
  title: "VideoFlow Adapter Test",
  concept: "Luxury K-beauty fashion short with cinematic retention rhythm",
  platform: "youtube_shorts",
  aspectRatio: "9:16",
  targetDurationSec: 35,
  musicBpm: 118,
  outputDir: "storage/test-videoflow-adapter",
  provider: { image: "hidream", video: "veo", motionFallback: "runway" }
});

const timeline = compileStoryboardToVideoFlow(storyboard);
const verification = verifyVideoFlowTimeline(timeline);

if (timeline.engine !== "videoflow") throw new Error("Timeline engine must be videoflow");
if (timeline.width !== 1080 || timeline.height !== 1920) throw new Error("9:16 canvas must compile to 1080x1920");
if (timeline.layers.length < storyboard.shots.length * 2) throw new Error("Each shot needs video and caption layers");
if (!timeline.layers.some((layer) => layer.type === "caption")) throw new Error("Caption layer missing");
if (!verification.passed) throw new Error(`VideoFlow verification failed: ${JSON.stringify(verification)}`);

console.log("VideoFlow adapter test passed:", {
  layers: timeline.layers.length,
  durationSec: timeline.durationSec,
  score: verification.score
});
