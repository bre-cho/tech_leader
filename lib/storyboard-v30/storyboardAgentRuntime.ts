import { writeJsonArtifact } from "@/lib/runtime/artifactStore";
import { StoryboardRequestSchema, type StoryboardOutput } from "./types";
import { planStoryboard } from "./storyboardPlanner";
import { runContinuityEngine } from "./continuityEngine";
import { buildRetentionPacingMap } from "./retentionEngine";
import { compileProviderBatches } from "./providerBatchCompiler";

export function runStoryboardAgentV30(raw: unknown): StoryboardOutput {
  const request = StoryboardRequestSchema.parse(raw);
  const phases = planStoryboard(request);
  const timeline = buildRetentionPacingMap(phases);
  const verification = runContinuityEngine(request, phases);
  const providerPayloads = compileProviderBatches(request, phases);

  const analysis = {
    sourceResearch: {
      facebookReelUrl: "https://www.facebook.com/reel/1980010219386918",
      fetchStatus: "Facebook reel could not be fetched by the browser tool due to throttling; analysis was grounded in the provided storyboard contact sheets.",
      observedStructure: [
        "I. SETUP: 01-25",
        "II. BACKSTAGE: 26-60",
        "III. RUNWAY: 61-130",
        "IV. AFTER PARTY: 131-160"
      ]
    },
    systemUpgrade: [
      "phase-aware 160-shot fashion event storyboard",
      "shot catalog with camera/movement/emotion/focus fields",
      "identity and wardrobe continuity contracts",
      "retention pacing map",
      "provider batch compilation for still keyframes + video shots",
      "runway rhythm logic: wide → detail → beauty close-up → reaction → pose → finale"
    ],
    shotCount: phases.flatMap(p => p.shots).length
  };

  const partial: StoryboardOutput = {
    status: verification.passed ? "ready" : "blocked",
    request,
    analysis,
    phases,
    timeline,
    providerPayloads,
    verification,
    artifacts: []
  };

  const artifact = writeJsonArtifact(request.outputDir, "v30_storyboard_agent_lfw_plan", partial, {
    title: request.title,
    location: request.location,
    shots: analysis.shotCount
  });
  partial.artifacts.push(artifact);

  return partial;
}
