import { writeJsonArtifact } from "@/lib/runtime/artifactStore";
import { StoryboardV31RequestSchema, type V31Output } from "./types";
import { createDefaultShortsShots } from "./defaultShortsShotFactory";
import { buildRhythmGraph } from "./rhythmGraphEngine";
import { validateEnergyCurve } from "./energyCurveValidator";
import { planMicroHooks } from "./microHookPlanner";
import { orchestrateRunwayEscalation } from "./runwayEscalationEngine";
import { validateFaceRetentionPriority } from "./faceRetentionPriority";
import { analyzeCameraLanguage } from "./cameraLanguageEngine";
import { analyzeAndInjectSocialProof } from "./socialProofInjector";
import { buildShortsRetentionGraph } from "./shortsTimelineEngine";
import { validateRetention } from "./retentionValidator";
import { compileProviderPayloads } from "./providerPayloadCompiler";

export function runStoryboardV31(raw: unknown): V31Output {
  const request = StoryboardV31RequestSchema.parse(raw);
  const shots = request.inputShots.length > 0
    ? request.inputShots
    : request.autoGenerateIfEmpty
      ? createDefaultShortsShots(request)
      : [];

  if (shots.length === 0) {
    throw new Error("No shots provided and autoGenerateIfEmpty=false.");
  }

  const rhythmGraph = buildRhythmGraph(shots);
  const energyValidation = validateEnergyCurve(rhythmGraph);
  const microHooks = planMicroHooks(shots, rhythmGraph);
  const runwayEscalation = orchestrateRunwayEscalation(shots);
  const faceRetention = validateFaceRetentionPriority(rhythmGraph);
  const cameraLanguage = analyzeCameraLanguage(shots);
  const socialProof = analyzeAndInjectSocialProof(shots, rhythmGraph);
  const shortsTimeline = buildShortsRetentionGraph(request);
  const retentionValidation = validateRetention(shots, rhythmGraph, shortsTimeline, request.targetDurationSec);
  const providerPayloads = compileProviderPayloads(request, shots, rhythmGraph);

  const checks = {
    energyCurve: Boolean((energyValidation as any).passed),
    microHooks: Boolean((microHooks as any).passed),
    runwayEscalation: Boolean((runwayEscalation as any).passed),
    faceRetention: Boolean((faceRetention as any).passed),
    cameraLanguage: Boolean((cameraLanguage as any).passed),
    socialProof: Boolean((socialProof as any).passed),
    retention: Boolean((retentionValidation as any).passed),
    providerPayloads: (providerPayloads.videoShots.items?.length ?? 0) === shots.length,
    renderQueue: (providerPayloads.renderQueue?.length ?? 0) === shots.length
  };

  const verification = {
    name: "StoryboardV31VerificationGate",
    passed: Object.values(checks).filter(Boolean).length / Object.keys(checks).length >= 0.75,
    score: Math.round(Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 100),
    checks,
    architecture: [
      "Concept",
      "Fashion DNA",
      "Music BPM",
      "Platform",
      "Phase Planner",
      "Rhythm Graph Engine",
      "Micro Hook Planner",
      "Camera Language Engine",
      "Runway Escalation Engine",
      "Social Proof Injector",
      "Retention Validator",
      "Provider Payload Compiler",
      "Render Queue"
    ]
  };

  const partial: V31Output = {
    status: verification.passed ? "ready" : "blocked",
    request,
    shots,
    rhythmGraph,
    energyValidation,
    microHooks,
    cameraLanguage,
    runwayEscalation,
    socialProof,
    shortsTimeline,
    retentionValidation,
    providerPayloads,
    verification,
    artifacts: []
  };

  const artifact = writeJsonArtifact(request.outputDir, "v31_storyboard_retention_rhythm_plan", partial, {
    title: request.title,
    platform: request.platform,
    shots: shots.length,
    verificationScore: verification.score
  });
  partial.artifacts.push(artifact);

  return partial;
}
