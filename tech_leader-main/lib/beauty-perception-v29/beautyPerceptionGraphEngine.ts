import { writeJsonArtifact } from "@/lib/runtime/artifactStore";
import { BeautyPerceptionRequestSchema, type BeautyPerceptionGraph, type BeautyPerceptionOutput, type EngineResult } from "./types";
import { buildBeautyDnaGraph } from "./beautyDnaGraph";
import { buildFemininitySignalGraph } from "./femininitySignalGraph";
import { runEyeContactEngine } from "./eyeContactEngine";
import { runHandToFacePsychologyEngine } from "./handToFacePsychology";
import { buildBeautyLightingGraph } from "./beautyLightingGraph";
import { runBeautyAttentionRoutingEngine } from "./attentionRoutingEngine";
import { runMicroExpressionEngine } from "./microExpressionEngine";
import { runBeautyVideoMotionEngine } from "./beautyVideoMotionEngine";
import { compileMultiReferenceSceneSpec } from "./multiReferencePromptCompiler";
import { routeBeautyProvider } from "./providerRouter";
import { runBeautyVerificationEngine } from "./beautyVerificationEngine";
import { runSocialBeautyCtrEngine } from "./socialBeautyCtrEngine";
import { calculateCommercialBeautyScore } from "./commercialBeautyScoring";
import { buildBeautyMemoryDna, saveBeautyMemoryDna } from "./beautyMemoryDna";

export function runBeautyPerceptionGraphEngine(raw: unknown): BeautyPerceptionOutput {
  const request = BeautyPerceptionRequestSchema.parse(raw);

  const beautyDnaGraph = buildBeautyDnaGraph(request);
  const femininitySignalGraph = buildFemininitySignalGraph(request);
  const eyeContact = runEyeContactEngine(request);
  const handToFace = runHandToFacePsychologyEngine(request);
  const lightingGraph = buildBeautyLightingGraph(request);
  const attentionRouting = runBeautyAttentionRoutingEngine(request);
  const microExpression = runMicroExpressionEngine(request);
  const videoMotion = runBeautyVideoMotionEngine(request);

  const baseEngines: Record<string, EngineResult> = {
    beautyDnaGraph,
    femininitySignalGraph,
    eyeContact,
    handToFace,
    lightingGraph,
    attentionRouting,
    microExpression,
    videoMotion
  };

  const multiReferenceCompiler = compileMultiReferenceSceneSpec(request, baseEngines);
  const providerRouter = routeBeautyProvider(request, lightingGraph);

  const negativePrompt = [
    "plastic skin",
    "dead eyes",
    "fake smile",
    "over symmetry",
    "collapsed anatomy",
    "drifted identity",
    "bad hands",
    "oversharpen",
    "AI texture",
    "fake teeth",
    "explicit nudity",
    "fetish framing",
    "voyeuristic angle",
    "underage subject"
  ].join(", ");

  const prompt = `
V29 Beauty Perception Graph Engine.

Brand: ${request.brandName}
Campaign: ${request.campaignName}
Product: ${request.productName ?? "no product"}
Platform: ${request.platform}
Target audience: ${request.targetAudience}

Commercial attractiveness psychology:
Beauty is not a pretty face. Beauty is an attention routing system.

${String(multiReferenceCompiler.data.prompt)}

Commercial scoring target:
trust + femininity + luxury + intimacy + realism + composition.

Video motion:
${JSON.stringify(videoMotion.data, null, 2)}

Provider route:
${JSON.stringify(providerRouter.data, null, 2)}

Quality requirements:
realistic skin texture, natural pores, believable smile, alive eyes, direct soft gaze, correct hands, preserved identity, commercial-safe beauty styling.
Avoid: ${negativePrompt}.
`.trim();

  const engines: Record<string, EngineResult> = {
    ...baseEngines,
    multiReferenceCompiler,
    providerRouter
  };

  const verification = runBeautyVerificationEngine(engines, `${prompt} ${negativePrompt}`);
  engines.verification = verification;

  const socialCtrPrediction = runSocialBeautyCtrEngine(request, engines);
  engines.socialCtr = socialCtrPrediction;

  const commercialBeautyScore = calculateCommercialBeautyScore(engines);
  const graph: BeautyPerceptionGraph = mergeGraph("v29_beauty_graph_" + Date.now(), [
    beautyDnaGraph,
    femininitySignalGraph
  ]);

  const sceneSpec = {
    ...(multiReferenceCompiler.data.sceneSpec as Record<string, unknown>),
    beauty_score: commercialBeautyScore,
    ctr_prediction: socialCtrPrediction.data,
    negative_prompt: negativePrompt
  };

  const promptPack = {
    prompt,
    negativePrompt,
    providerPayloads: {
      image: {
        providerRoute: providerRouter.data,
        prompt,
        negativePrompt,
        references: request.references,
        endpoint: (providerRouter.data as any).endpoints?.nano_banana
      },
      video: {
        prompt,
        negativePrompt,
        motionPlan: videoMotion.data,
        endpoint: (providerRouter.data as any).endpoints?.veo
      }
    }
  };

  const partial: Omit<BeautyPerceptionOutput, "memoryDna"> = {
    status: verification.score >= 90 && commercialBeautyScore.passed ? "ready" : "blocked",
    request,
    graph,
    engines,
    commercialBeautyScore,
    socialCtrPrediction,
    sceneSpec,
    providerRoute: providerRouter.data,
    promptPack,
    verification: verification.data,
    artifacts: []
  };

  const artifact = writeJsonArtifact(request.outputDir, "v29_beauty_perception_plan", partial, {
    brand: request.brandName,
    campaign: request.campaignName,
    engine: "V29 Beauty Perception Graph Engine"
  });
  partial.artifacts.push(artifact);

  let output: BeautyPerceptionOutput = partial;
  if (request.saveMemory && partial.status === "ready") {
    const dna = buildBeautyMemoryDna(request, partial);
    saveBeautyMemoryDna(dna);
    output = { ...partial, memoryDna: dna };
  }

  return output;
}

function mergeGraph(graph_id: string, engineResults: EngineResult[]): BeautyPerceptionGraph {
  const nodes = engineResults.flatMap(r => (r.data as any).nodes ?? []);
  const edges = engineResults.flatMap(r => (r.data as any).edges ?? []);
  const extraNodes = [
    { id: "trust", type: "Perception", label: "Trust", score: 94, properties: {} },
    { id: "femininity", type: "Perception", label: "Femininity", score: 94, properties: {} },
    { id: "luxury", type: "Perception", label: "Luxury", score: 92, properties: {} },
    { id: "intimacy", type: "Perception", label: "Intimacy", score: 90, properties: {} },
    { id: "attention_lock", type: "Perception", label: "Attention Lock", score: 95, properties: {} }
  ];
  return { graph_id, nodes: [...nodes, ...extraNodes], edges };
}
