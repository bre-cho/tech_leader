import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { createGoogleAiForCapability } from "./googleAiClientFactory";

function writeImage(outputDir: string, base64: string, mimeType = "image/png") {
  fs.mkdirSync(outputDir, { recursive: true });
  const buffer = Buffer.from(base64, "base64");
  const hash = crypto.createHash("sha256").update(buffer).digest("hex");
  const ext = mimeType.includes("jpeg") ? "jpg" : "png";
  const filePath = path.join(outputDir, `banana_${hash.slice(0, 16)}.${ext}`);
  fs.writeFileSync(filePath, buffer);
  return { path: filePath, checksum: hash, sizeBytes: buffer.length, mimeType };
}

export async function generateNanoBananaWithManagedAccount(params: {
  prompt: string;
  model?: string;
  aspectRatio?: string;
  imageSize?: string;
  sceneIndex?: number;
  outputDir?: string;
}) {
  const { ai, account } = createGoogleAiForCapability("nano_banana", params.sceneIndex ?? 0);
  const response: any = await ai.models.generateContent({
    model: params.model ?? "gemini-3.1-flash-image-preview",
    contents: params.prompt,
    config: {
      responseModalities: ["TEXT", "IMAGE"],
      imageConfig: {
        aspectRatio: params.aspectRatio ?? "4:5",
        imageSize: params.imageSize ?? "2K"
      }
    }
  } as any);

  const parts = response?.candidates?.[0]?.content?.parts ?? [];
  const textParts: string[] = [];
  const artifacts: any[] = [];

  for (const part of parts) {
    if (part.text) textParts.push(part.text);
    if (part.inlineData?.data) {
      artifacts.push(writeImage(params.outputDir ?? "storage/google-banana-managed", part.inlineData.data, part.inlineData.mimeType));
    }
  }

  return {
    status: "succeeded",
    provider: "google-nano-banana",
    account,
    model: params.model ?? "gemini-3.1-flash-image-preview",
    textParts,
    artifacts
  };
}
