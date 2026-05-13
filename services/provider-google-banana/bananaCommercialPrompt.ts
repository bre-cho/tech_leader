import type { BananaRequest } from "./bananaTypes";

export function compileBananaCommercialPrompt(req: BananaRequest): string {
  const base = req.prompt.trim();
  const negative = req.negativePrompt
    ? `\nAvoid: ${req.negativePrompt}.`
    : "\nAvoid: distorted text, wrong logos, unreadable typography, broken product shape, clutter, low quality.";

  const common = `
You are generating a commercial-grade visual for an AI Commercial Creative OS.

Commercial constraints:
- preserve subject/product consistency when references are provided
- make typography readable and brand-safe
- keep product hero clear
- use intentional attention routing: first glance → product desire → trust proof → CTA
- keep clean layout and platform-safe negative space
- output should be suitable for ${req.aspectRatio} aspect ratio and ${req.resolution} production preview
`.trim();

  if (req.mode === "commercial_poster") {
    return `${base}

${common}

Poster rules:
- strong headline zone
- product or avatar hero must be dominant
- premium commercial lighting
- billboard/social readability
- clean CTA area
${negative}`;
  }

  if (req.mode === "tiktok_creative") {
    return `${base}

${common}

TikTok creative rules:
- vertical short-form composition
- expressive first-frame hook
- face/product visible within first second
- leave safe zones for captions and UI
- motion-ready composition for poster-to-video
${negative}`;
  }

  if (req.mode === "upscale_8k") {
    return `${base}

${common}

Upscale/refine rules:
- preserve original identity, product, layout, text placement
- improve texture, sharpness, material realism
- do not invent new logos, new objects, or new text
- prepare clean 4K master suitable for downstream 8K upscaling
${negative}`;
  }

  return `${base}

${common}
${negative}`;
}
