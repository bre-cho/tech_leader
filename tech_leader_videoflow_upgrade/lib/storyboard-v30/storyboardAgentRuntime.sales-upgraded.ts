import { writeJsonArtifact } from "@/lib/runtime/artifactStore";
import { StoryboardRequestSchema, type StoryboardOutput } from "./types";
import { planStoryboard } from "./storyboardPlanner";
import { runContinuityEngine } from "./continuityEngine";
import { buildRetentionPacingMap } from "./retentionEngine";
import { compileProviderBatches } from "./providerBatchCompiler";
import { applySalesEngineToV30 } from "@/lib/storyboard-v30-sales/v30SalesAdapter";

export function runStoryboardAgentV30SalesUpgraded(raw: unknown): StoryboardOutput & {
  salesEngineV3?: Record<string, unknown>;
} {
  const request = StoryboardRequestSchema.parse(raw);
  let phases = planStoryboard(request);
  let timeline = buildRetentionPacingMap(phases);
  let verification = runContinuityEngine(request, phases) as Record<string, unknown>;
  let providerPayloads = compileProviderBatches(request, phases) as Record<string, unknown>;

  const salesEnhancement = applySalesEngineToV30({
    raw,
    request,
    phases,
    providerPayloads,
    verification
  });

  if (salesEnhancement) {
    phases = salesEnhancement.phases;
    timeline = buildRetentionPacingMap(phases);
    verification = salesEnhancement.verificationPatch;
    providerPayloads = salesEnhancement.providerPayloadsPatch;
  }

  const analysis = {
    sourceResearch: {
      basePatch: "v30_storyboard_agent_lfw_runway_full_patch",
      salesPatch: "AUTO_STORYBOARD_ENGINE_V3_SALES_PATCH",
      integration: "Sales mechanism routing injected into V30 phase-aware runway storyboard runtime.",
      observedStructure: [
        "I. SETUP: 01-25",
        "II. BACKSTAGE: 26-60",
        "III. RUNWAY: 61-130",
        "IV. AFTER PARTY: 131-160"
      ]
    },
    systemUpgrade: [
      "phase-aware fashion event storyboard",
      "AUTO STORYBOARD V3 sales mechanism detection",
      "commercial hook/desire/trust/proof/CTA injection",
      "product clarity scoring",
      "sales provider prompt compiler",
      "sales render queue",
      "sales verification gate",
      "runway rhythm + conversion overlay"
    ],
    shotCount: phases.flatMap((p) => p.shots).length,
    salesEngineEnabled: Boolean(salesEnhancement)
  };

  const basePassed = Boolean((verification as any).passed ?? true);
  const salesPassed = salesEnhancement ? Boolean((verification as any).salesEngineV3?.passed) : true;

  const partial: StoryboardOutput & { salesEngineV3?: Record<string, unknown> } = {
    status: basePassed && salesPassed ? "ready" : "blocked",
    request,
    analysis,
    phases,
    timeline,
    providerPayloads,
    verification,
    artifacts: [],
    ...(salesEnhancement ? { salesEngineV3: salesEnhancement.salesEngine as unknown as Record<string, unknown> } : {})
  };

  const artifact = writeJsonArtifact(request.outputDir, "v30_sales_upgraded_storyboard_plan", partial, {
    title: request.title,
    location: request.location,
    shots: analysis.shotCount,
    salesEngineEnabled: Boolean(salesEnhancement)
  });
  partial.artifacts.push(artifact);

  return partial;
}
