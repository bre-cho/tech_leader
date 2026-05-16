import { GoogleGenAI } from "@google/genai";
import fs from "node:fs";
import type { BananaRequest, BananaResponse } from "./bananaTypes";
import { compileBananaCommercialPrompt } from "./bananaCommercialPrompt";
import { buildConsistencyMemory } from "./bananaConsistency";
import { scoreBananaCommercial } from "./bananaCommercialScoring";
import { writeBananaArtifact, writeManifest } from "./bananaArtifactStore";
import { validateBananaSafety } from "./bananaSafety";
import { withBananaRetry } from "./bananaRetry";
import { bananaRateLimit } from "./bananaRateLimit";
import { resolveGoogleAiForCapability } from "@/services/google-ai/googleAiClientFactory";

export class GoogleBananaClient {
  private ai: GoogleGenAI;

  constructor(apiKey?: string) {
    const resolvedApiKey = apiKey || (() => {
      try {
        return resolveGoogleAiForCapability("nano_banana").apiKey;
      } catch {
        return process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
      }
    })();

    if (!resolvedApiKey) {
      throw new Error("Missing GEMINI_API_KEY or GOOGLE_API_KEY.");
    }
    this.ai = new GoogleGenAI({ apiKey: resolvedApiKey });
  }

  async run(req: BananaRequest): Promise<BananaResponse> {
    validateBananaSafety(req);
    bananaRateLimit("google-banana");

    const consistency = buildConsistencyMemory(req);
    const prompt = `${compileBananaCommercialPrompt(req)}\n\n${consistency.promptInjection}`;

    const contents: any[] = [{ text: prompt }];
    for (const image of req.images) {
      contents.push({
        inlineData: {
          mimeType: image.mimeType,
          data: image.dataBase64
        }
      });
    }

    const response: any = await withBananaRetry(() =>
      this.ai.models.generateContent({
        model: req.model,
        contents,
        config: {
          responseModalities: ["TEXT", "IMAGE"],
          ...(req.aspectRatio || req.resolution ? {
            imageConfig: {
              aspectRatio: req.aspectRatio,
              imageSize: req.resolution
            }
          } : {})
        }
      } as any)
    );

    const textParts: string[] = [];
    const artifacts = [];

    const parts =
      response?.candidates?.[0]?.content?.parts ??
      response?.parts ??
      [];

    for (const part of parts) {
      if (part.text) {
        textParts.push(part.text);
      }
      if (part.inlineData?.data) {
        const mimeType = part.inlineData.mimeType ?? "image/png";
        const ext = mimeType.includes("jpeg") ? "jpg" : "png";
        const buffer = Buffer.from(part.inlineData.data, "base64");
        artifacts.push(writeBananaArtifact({
          outputDir: req.outputDir,
          buffer,
          extension: ext,
          mimeType,
          model: req.model,
          metadata: {
            mode: req.mode,
            aspectRatio: req.aspectRatio,
            resolution: req.resolution,
            consistency,
            requestMetadata: req.metadata
          }
        }));
      }
    }

    const scoring = scoreBananaCommercial(req, artifacts);
    const manifest = writeManifest(req.outputDir, { req, scoring, artifacts, textParts }, req.model);
    artifacts.push(manifest);

    const winnerDnaCandidate = scoring.winner_dna_ready ? {
      provider: "google-banana",
      model: req.model,
      mode: req.mode,
      prompt,
      referenceCount: req.images.length,
      scoring
    } : undefined;

    return {
      status: "succeeded",
      mode: req.mode,
      model: req.model,
      textParts,
      artifacts,
      scoring,
      winnerDnaCandidate,
      rawUsage: response?.usageMetadata ?? {}
    };
  }
}

export function imageFileToBananaInput(filePath: string, label?: string) {
  const dataBase64 = fs.readFileSync(filePath).toString("base64");
  const lower = filePath.toLowerCase();
  const mimeType = lower.endsWith(".jpg") || lower.endsWith(".jpeg") ? "image/jpeg" : "image/png";
  return { mimeType, dataBase64, label };
}
