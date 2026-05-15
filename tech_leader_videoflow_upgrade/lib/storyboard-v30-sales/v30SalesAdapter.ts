import type { PhasePlan, ShotSpec, StoryboardRequest } from "@/lib/storyboard-v30/types";
import { generateSalesStoryboardV3ForV30 } from "./salesPipeline";
import { SalesStoryboardInputSchema, type SalesStoryboardInput, type SalesStoryboardOutput } from "./types";

export type SalesEnhancedV30Result = {
  salesEngine: SalesStoryboardOutput;
  phases: PhasePlan[];
  providerPayloadsPatch: Record<string, unknown>;
  verificationPatch: Record<string, unknown>;
};

export function maybeParseSalesEngine(raw: unknown): SalesStoryboardInput | null {
  if (!raw || typeof raw !== "object") return null;
  const candidate = (raw as any).salesEngine;
  if (!candidate || candidate.enabled === false) return null;
  return SalesStoryboardInputSchema.parse(candidate);
}

export function applySalesEngineToV30(params: {
  raw: unknown;
  request: StoryboardRequest;
  phases: PhasePlan[];
  providerPayloads: Record<string, unknown>;
  verification: Record<string, unknown>;
}): SalesEnhancedV30Result | null {
  const input = maybeParseSalesEngine(params.raw);
  if (!input) return null;

  const salesEngine = generateSalesStoryboardV3ForV30(input);
  const phases = injectSalesLogicIntoPhases(params.phases, salesEngine, params.request);
  const providerPayloadsPatch = buildSalesProviderPayloadPatch(params.providerPayloads, salesEngine, params.request);
  const verificationPatch = buildSalesVerificationPatch(params.verification, salesEngine, phases);

  return { salesEngine, phases, providerPayloadsPatch, verificationPatch };
}

function injectSalesLogicIntoPhases(phases: PhasePlan[], sales: SalesStoryboardOutput, request: StoryboardRequest): PhasePlan[] {
  const salesShots = sales.scenes.map((scene, idx): ShotSpec => {
    const providerPrompt = sales.providerPrompts[idx];
    return {
      id: 9000 + idx + 1,
      phase: idx === 0 ? "setup" : idx === sales.scenes.length - 1 ? "after_party" : "runway",
      title: `SALES ${scene.scenePurpose.toUpperCase()} — ${sales.input.productName}`,
      description: `${scene.visual}. ${scene.action}`,
      camera: scene.camera,
      lens: scene.scenePurpose === "proof" || scene.scenePurpose === "desire" ? "85mm / 100mm macro commercial lens" : "35mm social commercial lens",
      movement: scene.motion,
      durationSec: scene.durationSec,
      subjectFocus: sales.decision.priority.join(" → "),
      emotionBeat: scene.scenePurpose,
      continuityTags: [
        `sales:${sales.decision.mechanism}`,
        `category:${sales.decision.category}`,
        `product:${sales.input.productName}`,
        `storyArc:${sales.decision.storyArc}`
      ],
      prompt: providerPrompt.prompt,
      negativePrompt: providerPrompt.negativePrompt,
      providerPayload: {
        endpoint: "/api/providers/video/generate",
        provider: providerPrompt.provider,
        prompt: providerPrompt.prompt,
        negativePrompt: providerPrompt.negativePrompt,
        settings: providerPrompt.settings
      }
    };
  });

  return phases.map((phase) => {
    const phaseSalesShots = salesShots.filter((shot) => shot.phase === phase.phase);
    if (phaseSalesShots.length === 0) return phase;

    const shots = phase.phase === "setup"
      ? [...phaseSalesShots, ...phase.shots]
      : phase.phase === "after_party"
        ? [...phase.shots, ...phaseSalesShots]
        : interleaveCommercialBeats(phase.shots, phaseSalesShots);

    return {
      ...phase,
      purpose: `${phase.purpose} Sales overlay: ${sales.decision.visualHook}.`,
      retentionRole: `${phase.retentionRole} Commercial objective: ${sales.decision.storyArc} / ${sales.score.verdict}.`,
      startShot: shots[0]?.id ?? phase.startShot,
      endShot: shots[shots.length - 1]?.id ?? phase.endShot,
      shots
    };
  });
}

function interleaveCommercialBeats(existing: ShotSpec[], salesShots: ShotSpec[]) {
  if (salesShots.length === 0) return existing;
  const output: ShotSpec[] = [];
  const spacing = Math.max(1, Math.floor(existing.length / (salesShots.length + 1)));
  let salesIndex = 0;
  existing.forEach((shot, idx) => {
    output.push(shot);
    if ((idx + 1) % spacing === 0 && salesIndex < salesShots.length) {
      output.push(salesShots[salesIndex++]);
    }
  });
  while (salesIndex < salesShots.length) output.push(salesShots[salesIndex++]);
  return output;
}

function buildSalesProviderPayloadPatch(providerPayloads: Record<string, unknown>, sales: SalesStoryboardOutput, request: StoryboardRequest) {
  const salesVideoItems = sales.providerPrompts.map((prompt, idx) => ({
    shotId: `sales_${idx + 1}`,
    phase: sales.scenes[idx].scenePurpose,
    provider: prompt.provider,
    endpoint:
      prompt.provider === "veo" ? "/api/providers/google-managed/veo/generate" :
      prompt.provider === "runway" ? "/api/providers/runway/generate" :
      prompt.provider === "kling" ? "/api/providers/kling/generate" :
      prompt.provider === "seedance" ? "/api/providers/seedance/generate" :
      "/api/providers/video/generate",
    prompt: prompt.prompt,
    negativePrompt: prompt.negativePrompt,
    durationSec: sales.scenes[idx].durationSec,
    aspectRatio: sales.input.aspectRatio || request.aspectRatio,
    settings: prompt.settings
  }));

  const salesKeyframes = sales.providerPrompts.map((prompt, idx) => ({
    shotId: `sales_keyframe_${idx + 1}`,
    provider: sales.decision.category === "fashion" ? "hidream" : "banana",
    endpoint: sales.decision.category === "fashion" ? "/api/v1/hidream/commercial-visual/generate" : "/api/providers/google-managed/nano-banana/generate",
    prompt: prompt.prompt,
    negativePrompt: prompt.negativePrompt,
    aspectRatio: sales.input.aspectRatio || request.aspectRatio,
    settings: prompt.settings
  }));

  return {
    ...providerPayloads,
    salesEngineV3: {
      decision: sales.decision,
      score: sales.score,
      scenes: sales.scenes,
      providerPrompts: sales.providerPrompts
    },
    salesVideoShots: {
      provider: "mixed",
      items: salesVideoItems
    },
    salesKeyframes: {
      provider: "banana/hidream",
      items: salesKeyframes
    },
    renderQueueSales: salesVideoItems.map((item) => ({
      jobType: "sales_storyboard_v3_video_scene",
      shotId: item.shotId,
      provider: item.provider,
      endpoint: item.endpoint,
      payload: item,
      retryPolicy: { maxAttempts: 3, backoffMs: [1000, 3000, 8000] }
    }))
  };
}

function buildSalesVerificationPatch(verification: Record<string, unknown>, sales: SalesStoryboardOutput, phases: PhasePlan[]) {
  const checks = {
    sales_engine_ready: sales.score.verdict === "READY" || sales.score.verdict === "TEST",
    has_sales_hook: sales.scenes.some((s) => s.scenePurpose === "hook"),
    has_sales_cta: sales.scenes.some((s) => s.scenePurpose === "cta"),
    product_clarity_ok: sales.score.productClarity >= 85,
    conversion_ok: sales.score.conversion >= 85,
    all_sales_prompts_compiled: sales.providerPrompts.length === sales.scenes.length,
    sales_shots_injected: phases.flatMap((p) => p.shots).some((s) => s.id >= 9000)
  };
  const score = Math.round(Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 100);
  return {
    ...verification,
    salesEngineV3: {
      passed: score >= 85,
      score,
      checks,
      verdict: sales.score.verdict,
      finalSalesScore: sales.score.finalScore,
      reasons: sales.score.reasons
    }
  };
}
