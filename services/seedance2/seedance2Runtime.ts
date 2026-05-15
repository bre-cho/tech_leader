import fs from "node:fs";
import path from "node:path";

function parseResponseBody(contentType: string | null, rawBody: string) {
  if (contentType?.includes("application/json")) {
    try {
      return JSON.parse(rawBody);
    } catch {
      return { rawBody };
    }
  }
  return { rawBody };
}

export async function generateSeedance2Video(params: {
  prompt: string;
  imageUri?: string;
  model?: string;
  durationSec?: number;
  aspectRatio?: string;
  mode?: "text_to_video" | "image_to_video";
  outputDir?: string;
  extra?: Record<string, unknown>;
}) {
  const apiKey = process.env.SEEDANCE_API_KEY;
  if (!apiKey) {
    throw new Error("Missing SEEDANCE_API_KEY.");
  }

  const apiUrl = process.env.SEEDANCE_API_URL || "https://api.seedance.ai/v1/video/generations";
  const payload: Record<string, unknown> = {
    prompt: params.prompt,
    model: params.model ?? "seedance-2",
    mode: params.mode ?? (params.imageUri ? "image_to_video" : "text_to_video"),
    duration: params.durationSec ?? 6,
    aspect_ratio: params.aspectRatio ?? "16:9",
    ...(params.imageUri ? { image_url: params.imageUri } : {}),
    ...(params.extra ?? {})
  };

  const response = await fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify(payload)
  });

  const rawBody = await response.text();
  const body = parseResponseBody(response.headers.get("content-type"), rawBody);

  const outputDir = params.outputDir ?? "storage/seedance2-managed";
  fs.mkdirSync(outputDir, { recursive: true });
  const manifestPath = path.join(outputDir, `seedance2_operation_${Date.now()}.json`);
  fs.writeFileSync(
    manifestPath,
    JSON.stringify({ apiUrl, request: payload, status: response.status, response: body }, null, 2),
    "utf8"
  );

  if (!response.ok) {
    throw new Error(`Seedance2 API failed (${response.status}): ${rawBody}`);
  }

  return {
    status: "operation_started",
    provider: "seedance2",
    model: payload.model,
    operation: body,
    manifestPath
  };
}
