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

export async function generateKlingVideo(params: {
  prompt: string;
  imageUri?: string;
  model?: string;
  durationSec?: number;
  aspectRatio?: string;
  negativePrompt?: string;
  outputDir?: string;
  extra?: Record<string, unknown>;
}) {
  const apiKey = process.env.KLING_API_KEY;
  if (!apiKey) {
    throw new Error("Missing KLING_API_KEY.");
  }

  const apiUrl = process.env.KLING_API_URL || "https://api.klingai.com/v1/videos/generations";
  const payload: Record<string, unknown> = {
    prompt: params.prompt,
    model: params.model ?? "kling-v1",
    duration: params.durationSec ?? 6,
    aspect_ratio: params.aspectRatio ?? "16:9",
    ...(params.negativePrompt ? { negative_prompt: params.negativePrompt } : {}),
    ...(params.imageUri ? { image: { url: params.imageUri } } : {}),
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

  const outputDir = params.outputDir ?? "storage/kling-managed";
  fs.mkdirSync(outputDir, { recursive: true });
  const manifestPath = path.join(outputDir, `kling_operation_${Date.now()}.json`);
  fs.writeFileSync(
    manifestPath,
    JSON.stringify({ apiUrl, request: payload, status: response.status, response: body }, null, 2),
    "utf8"
  );

  if (!response.ok) {
    throw new Error(`Kling API failed (${response.status}): ${rawBody}`);
  }

  return {
    status: "operation_started",
    provider: "kling",
    model: payload.model,
    operation: body,
    manifestPath
  };
}
