import { writeJsonArtifact } from "@/lib/runtime/artifactStore";
import { BeautyIdentityRuntimeRequestSchema, type BeautyIdentityRuntimeOutput } from "./types";
import { extractBeautyIdentityDna } from "./identityDnaExtractor";
import { buildFaceLockContract } from "./faceLockContract";
import { buildVisualRecipe } from "./visualRecipeLibrary";
import { routeProvider } from "./providerRouter";
import { compileIdentityLockedPromptPack } from "./promptCompiler";
import { runIdentityBeautyQualityGate } from "./qualityGate";
import { buildIdentityWinnerDna, saveIdentityWinnerDna } from "./winnerDna";

export function runIdentityBeautyRuntime(raw: unknown): BeautyIdentityRuntimeOutput {
  const request = BeautyIdentityRuntimeRequestSchema.parse(raw);

  const identityDna = extractBeautyIdentityDna(request);
  const faceLockContract = buildFaceLockContract(request);
  const visualRecipe = buildVisualRecipe(request);
  const providerRoute = routeProvider(request, visualRecipe);
  const promptPack = compileIdentityLockedPromptPack({ req: request, identityDna, faceLockContract, visualRecipe, providerRoute });
  const qaReport = runIdentityBeautyQualityGate({ req: request, identityDna, faceLockContract, visualRecipe, promptPack });

  const providerPayloads = {
    stillImage: (promptPack.data as any).providerPayload,
    videoKeyframe: {
      ...(promptPack.data as any).providerPayload,
      endpoint: "/api/providers/google-managed/veo/generate",
      motion: {
        eyeContact: "direct soft gaze",
        microSmile: "natural tiny smile drift",
        breathing: "subtle",
        hairMotion: "very soft",
        bodyMotion: "commercial-safe natural motion"
      }
    },
    postProcess: {
      faceDetailer: true,
      skinTextureGuard: true,
      watermarkRemovalDisabled: false,
      artifactValidation: true
    }
  };

  const partial: Omit<BeautyIdentityRuntimeOutput, "winnerDna"> = {
    status: qaReport.score >= 90 ? "ready" : "blocked",
    request,
    identityDna,
    faceLockContract,
    visualRecipe,
    providerRoute,
    promptPack,
    qaReport,
    providerPayloads,
    artifacts: []
  };

  const artifact = writeJsonArtifact(request.output.outputDir, "v29_1_identity_beauty_runtime_plan", partial, {
    brand: request.brandName,
    visualIntent: request.visualIntent,
    provider: (providerRoute.data as any).selected
  });
  partial.artifacts.push(artifact);

  let output: BeautyIdentityRuntimeOutput = partial;
  if (request.saveWinnerDna && partial.status === "ready") {
    const dna = buildIdentityWinnerDna(request, partial);
    saveIdentityWinnerDna(dna);
    output = { ...partial, winnerDna: dna };
  }

  return output;
}
