import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

export type ArtifactContract = {
  artifact_id: string;
  artifact_type: string;
  path: string;
  mime_type: string;
  size_bytes: number;
  checksum_sha256: string;
  created_at: string;
  metadata: Record<string, unknown>;
};

export function sha256(value: Buffer | string) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

export function writeJsonArtifact(outputDir: string, artifactType: string, payload: unknown, metadata: Record<string, unknown> = {}): ArtifactContract {
  fs.mkdirSync(outputDir, { recursive: true });
  const body = Buffer.from(JSON.stringify(payload, null, 2), "utf8");
  const checksum = sha256(body);
  const filePath = path.join(outputDir, `${artifactType}_${checksum.slice(0, 12)}.json`);
  fs.writeFileSync(filePath, body);
  const stat = fs.statSync(filePath);
  return {
    artifact_id: `art_${checksum.slice(0, 16)}`,
    artifact_type: artifactType,
    path: filePath,
    mime_type: "application/json",
    size_bytes: stat.size,
    checksum_sha256: checksum,
    created_at: new Date().toISOString(),
    metadata
  };
}

export function appendJsonl(filePath: string, data: Record<string, unknown>) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.appendFileSync(filePath, JSON.stringify(data) + "\n", "utf8");
}
