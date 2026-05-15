import fs from "node:fs";
import path from "node:path";
import { createGoogleAiForCapability } from "./googleAiClientFactory";

export async function generateVeo31WithManagedAccount(params: {
  prompt: string;
  model?: string;
  sceneIndex?: number;
  outputDir?: string;
  config?: Record<string, unknown>;
}) {
  const { ai, account } = createGoogleAiForCapability("veo_3_1", params.sceneIndex ?? 0);
  const model = params.model ?? "veo-3.1-generate-preview";

  // The Gemini SDK uses long-running operations for Veo.
  const operation: any = await (ai.models as any).generateVideos({
    model,
    prompt: params.prompt,
    config: params.config ?? {
      aspectRatio: "16:9",
      resolution: "1080p",
      durationSeconds: 8
    }
  });

  const outputDir = params.outputDir ?? "storage/veo-managed";
  fs.mkdirSync(outputDir, { recursive: true });
  const manifestPath = path.join(outputDir, `veo_operation_${Date.now()}.json`);
  fs.writeFileSync(manifestPath, JSON.stringify(operation, null, 2), "utf8");

  return {
    status: "operation_started",
    provider: "google-veo-3.1",
    account,
    model,
    operation,
    manifestPath,
    note: "Poll/download operation result with your existing Veo worker/runtime."
  };
}
