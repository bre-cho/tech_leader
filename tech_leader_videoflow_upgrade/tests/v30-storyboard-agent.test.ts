import { runStoryboardAgentV30 } from "../lib/storyboard-v30/storyboardAgentRuntime";

const result = runStoryboardAgentV30({
  title: "London Fashion Week Test",
  format: "fashion_runway",
  totalShots: 160,
  targetDurationSec: 240,
  requestedPhases: ["setup", "backstage", "runway", "after_party"],
  mainCharacter: "1 cô gái",
  location: "London Fashion Week",
  aspectRatio: "1:1",
  outputDir: "storage/test-v30-storyboard",
  providers: { still: "hidream", video: "veo", motionAlt: "runway" }
});

const shots = result.phases.flatMap(p => p.shots);
if (result.status !== "ready") throw new Error("Storyboard should be ready");
if (shots.length !== 160) throw new Error(`Expected 160 shots, got ${shots.length}`);
if (!result.phases.find(p => p.phase === "runway")) throw new Error("Runway phase missing");
if (!shots.every(s => s.providerPayload.endpoint)) throw new Error("Provider payload endpoint missing");
if (!shots[0].prompt.includes("same female model face identity")) throw new Error("Continuity prompt missing");
if ((result.timeline as any).totalDurationSec <= 0) throw new Error("Timeline duration missing");

console.log("V30 Storyboard Agent test passed:", shots.length, "shots");
