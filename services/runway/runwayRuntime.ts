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

export async function generateRunwayVideo(params: {
  prompt: string;
  imageUri?: string;
  model?: string;
  durationSec?: number;
  ratio?: string;
  outputDir?: string;
  extra?: Record<string, unknown>;
}) {
  const apiKey = process.env.RUNWAY_API_KEY;
  if (!apiKey) {
    throw new Error("Missing RUNWAY_API_KEY.");
  }

  const apiUrl = process.env.RUNWAY_API_URL || "https://api.dev.runwayml.com/v1/image_to_video";
  const payload: Record<string, unknown> = {
    promptText: params.prompt,
    model: params.model ?? "gen4_turbo",
    ratio: params.ratio ?? "1280:720",
    duration: params.durationSec ?? 6,
    ...(params.imageUri ? { imageUri: params.imageUri } : {}),
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

  const outputDir = params.outputDir ?? "storage/runway-managed";
  fs.mkdirSync(outputDir, { recursive: true });
  const manifestPath = path.join(outputDir, `runway_operation_${Date.now()}.json`);
  fs.writeFileSync(
    manifestPath,
    JSON.stringify({ apiUrl, request: payload, status: response.status, response: body }, null, 2),
    "utf8"
  );

  if (!response.ok) {
    throw new Error(`Runway API failed (${response.status}): ${rawBody}`);
  }

  return {
    status: "operation_started",
    provider: "runway",
    model: payload.model,
    operation: body,
    manifestPath
  };
}
