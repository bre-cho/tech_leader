import { writeJsonArtifact } from "@/lib/runtime/artifactStore";
import { BeautyCommerceInputSchema, type BeautyCommerceOutput } from "./types";
import { buildBananaMultiReferenceEngine } from "./bananaMultiReferenceEngine";
import { runFemininityBeautyCommerceEngine } from "./femininityCommerceEngine";
import { runSocialBeautyCommerceVideoEngine, buildVideoPlan } from "./socialBeautyVideoEngine";
import { routeBeautyCommerceProvider } from "./providerRouter";
import { compileBeautyCommercePrompt } from "./promptCompiler";
import { verifyBeautyCommerceV28, scoreCommercialV28 } from "./verification";
import { buildWinnerDna, saveWinnerDna } from "./winnerDna";

export function runBeautyCommerceV28(raw: unknown): BeautyCommerceOutput {
  const input = BeautyCommerceInputSchema.parse(raw);

  const bananaMultiReference = buildBananaMultiReferenceEngine(input);
  const femininityEngine = runFemininityBeautyCommerceEngine(input);
  const videoEngine = runSocialBeautyCommerceVideoEngine(input);
  const videoPlan = buildVideoPlan(input, videoEngine);
  const providerRoute = routeBeautyCommerceProvider(input);

  const { prompt, negativePrompt } = compileBeautyCommercePrompt(input, {
    bananaMultiReference,
    femininityEngine,
    videoEngine
  }, videoPlan);

  const verification = verifyBeautyCommerceV28({
    bananaMultiReference,
    femininityEngine,
    videoEngine,
    prompt,
    negativePrompt,
    videoPlan
  });

  const commercialScore = scoreCommercialV28(verification, input);

  const providerPayloads = {
    image: {
      endpoint: providerRoute.imageProvider === "banana"
        ? "/api/providers/google-managed/nano-banana/generate"
        : providerRoute.imageProvider === "hidream"
          ? "/api/v1/hidream/commercial-visual/generate"
          : "/api/providers/image/generate",
      provider: providerRoute.imageProvider,
      prompt,
      negativePrompt,
      references: input.references,
      outputDir: input.outputDir,
      sceneIndex: 0,
      aspectRatio: input.channel === "poster" ? "4:5" : "9:16"
    },
    video: {
      endpoint: providerRoute.videoProvider === "veo"
        ? "/api/providers/google-managed/veo/generate"
        : providerRoute.videoProvider === "ltx"
          ? "/api/v1/creative-execution/lipdub-workflow"
          : "/api/providers/video/generate",
      provider: providerRoute.videoProvider,
      prompt,
      negativePrompt,
      videoPlan,
      outputDir: input.outputDir
    },
    postprocess: {
      lipdub: videoPlan.handoff.lipdub,
      subtitleKaraoke: videoPlan.handoff.subtitles,
      voice: videoPlan.handoff.voice
    }
  };

  const partial: any = {
    status: verification.passed && commercialScore.pass ? "ready" : "blocked",
    input,
    bananaMultiReference,
    femininityEngine,
    videoEngine,
    providerRoute,
    prompt,
    negativePrompt,
    videoPlan,
    verification,
    commercialScore,
    providerPayloads,
    artifacts: []
  };

  const artifact = writeJsonArtifact(input.outputDir, "beauty_commerce_v28_plan", partial, {
    engine: "V28.2+V28.3",
    brand: input.brandName,
    channel: input.channel
  });
  partial.artifacts.push(artifact);

  if (input.saveWinnerDna && commercialScore.winner_dna_ready && verification.passed) {
    const dna = buildWinnerDna(input, partial);
    saveWinnerDna(dna);
    partial.winnerDna = dna;
  }

  return partial as BeautyCommerceOutput;
}
