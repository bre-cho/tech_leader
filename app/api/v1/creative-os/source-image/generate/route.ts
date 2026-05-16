import fs from "node:fs";
import path from "node:path";
import { NextRequest, NextResponse } from "next/server";
import { bananaImageGenerate } from "@/services/provider-google-banana/bananaImageGenerate";

type GenerateBody = {
  prompt?: string;
  negativePrompt?: string;
  model?: string;
  aspectRatio?: string;
  resolution?: "1K" | "2K" | "4K";
};

function createMockPreviewDataUrl(prompt: string): string {
  const safePrompt = prompt
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1500" viewBox="0 0 1200 1500">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#1a1208" />
          <stop offset="50%" stop-color="#6b4a18" />
          <stop offset="100%" stop-color="#120f0b" />
        </linearGradient>
        <radialGradient id="glow" cx="50%" cy="35%" r="45%">
          <stop offset="0%" stop-color="#f6d57a" stop-opacity="0.95" />
          <stop offset="100%" stop-color="#f6d57a" stop-opacity="0" />
        </radialGradient>
      </defs>
      <rect width="1200" height="1500" fill="url(#bg)" />
      <rect width="1200" height="1500" fill="url(#glow)" />
      <rect x="250" y="230" width="700" height="1040" rx="42" fill="rgba(255,255,255,0.06)" stroke="rgba(246,213,122,0.35)" />
      <circle cx="600" cy="580" r="190" fill="rgba(255,255,255,0.08)" stroke="rgba(246,213,122,0.45)" />
      <rect x="520" y="450" width="160" height="360" rx="36" fill="#d6b36a" opacity="0.88" />
      <rect x="548" y="390" width="104" height="78" rx="18" fill="#f3deb0" opacity="0.95" />
      <text x="600" y="1085" text-anchor="middle" fill="#fff6e8" font-family="Arial, sans-serif" font-size="42" font-weight="700">Creative OS Mock Preview</text>
      <foreignObject x="180" y="1135" width="840" height="210">
        <div xmlns="http://www.w3.org/1999/xhtml" style="color:#fff6e8;font-family:Arial,sans-serif;font-size:28px;line-height:1.45;text-align:center;padding:0 24px;">
          ${safePrompt}
        </div>
      </foreignObject>
    </svg>`;

  return `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as GenerateBody;
    const prompt = body.prompt?.trim();

    if (!prompt || prompt.length < 3) {
      return NextResponse.json({ detail: "Prompt must be at least 3 characters." }, { status: 400 });
    }

    if (!process.env.GEMINI_API_KEY && !process.env.GOOGLE_API_KEY) {
      return NextResponse.json({
        status: "succeeded",
        prompt,
        image_url: createMockPreviewDataUrl(prompt),
        artifact_path: "mock://creative-os/source-image.svg",
        model: "mock-local-preview",
        is_mock: true,
      });
    }

    const result = await bananaImageGenerate({
      mode: "generate",
      prompt,
      negativePrompt: body.negativePrompt,
      model: body.model,
      aspectRatio: body.aspectRatio || "4:5",
      resolution: body.resolution || "2K",
      outputDir: "storage/google-banana/creative-os-source",
      metadata: {
        surface: "creative-os-control-plane",
        workflow: "source-image-generate",
      },
    });

    const imageArtifact = result.artifacts.find((artifact) => artifact.type === "image");
    if (!imageArtifact) {
      return NextResponse.json({ detail: "No image artifact returned from generator." }, { status: 502 });
    }

    const artifactPath = path.resolve(process.cwd(), imageArtifact.path);
    const base64 = fs.readFileSync(artifactPath).toString("base64");
    const previewDataUrl = `data:${imageArtifact.mimeType};base64,${base64}`;

    return NextResponse.json({
      status: result.status,
      prompt,
      image_url: previewDataUrl,
      artifact_path: imageArtifact.path,
      model: result.model,
      is_mock: false,
    });
  } catch (error) {
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : "Source image generation failed." },
      { status: 500 },
    );
  }
}
