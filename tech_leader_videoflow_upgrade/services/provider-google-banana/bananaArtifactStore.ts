import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import type { BananaArtifact } from "./bananaTypes";

export function sha256(buffer: Buffer | string) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

export function ensureDir(dir: string) {
  fs.mkdirSync(dir, { recursive: true });
}

export function writeBananaArtifact(params: {
  outputDir: string;
  buffer: Buffer;
  extension: string;
  mimeType: string;
  model: string;
  metadata?: Record<string, unknown>;
}): BananaArtifact {
  ensureDir(params.outputDir);
  const checksum = sha256(params.buffer);
  const filename = `banana_${checksum.slice(0, 16)}.${params.extension}`;
  const filePath = path.join(params.outputDir, filename);
  fs.writeFileSync(filePath, params.buffer);
  const stat = fs.statSync(filePath);

  return {
    artifactId: `art_${checksum.slice(0, 16)}`,
    type: params.mimeType.startsWith("image/") ? "image" : "text",
    path: filePath,
    mimeType: params.mimeType,
    sizeBytes: stat.size,
    checksumSha256: checksum,
    provider: "google-banana",
    model: params.model,
    metadata: params.metadata ?? {}
  };
}

export function writeManifest(outputDir: string, payload: unknown, model: string): BananaArtifact {
  const buffer = Buffer.from(JSON.stringify(payload, null, 2), "utf8");
  return writeBananaArtifact({
    outputDir,
    buffer,
    extension: "json",
    mimeType: "application/json",
    model,
    metadata: { artifactKind: "manifest" }
  });
}
