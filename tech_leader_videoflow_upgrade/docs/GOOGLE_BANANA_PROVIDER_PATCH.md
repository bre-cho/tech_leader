# Google Banana Provider Patch

## Official model IDs

Google's image generation docs define Nano Banana models:

- `gemini-3.1-flash-image-preview` — Nano Banana 2
- `gemini-3-pro-image-preview` — Nano Banana Pro
- `gemini-2.5-flash-image` — Nano Banana stable speed/efficiency model

## Why this provider belongs in MVP

Google Banana should become the commercial default provider for:

- beauty ads
- FMCG
- TikTok ads
- billboard
- poster
- fashion
- luxury branding
- product hero ads

## Runtime architecture

```text
Creative Workflow Graph
→ Provider Router
→ Google Nano Banana Provider
→ Commercial Visual Reasoning
→ Attention Routing
→ Poster / Billboard / TikTok Runtime
→ Memory Update
→ Winner DNA
```

## API

```text
POST /api/providers/google-banana/generate
POST /api/providers/google-banana/edit
POST /api/providers/google-banana/multi-reference
POST /api/providers/google-banana/commercial-poster
POST /api/providers/google-banana/tiktok-creative
POST /api/providers/google-banana/8k-upscale
```

## Env

```bash
GEMINI_API_KEY=...
```

## Install

```bash
npm install @google/genai zod
npm run typecheck
npm run test:banana
```

## Production notes

- Use `gemini-3.1-flash-image-preview` for high-volume commercial images.
- Use `gemini-3-pro-image-preview` for professional asset production and high-fidelity text.
- Use `gemini-2.5-flash-image` for stable low-latency generation.
- Generated images include SynthID watermark according to Google docs.
- Final 8K should be handled by your upscale runtime after Banana outputs 2K/4K master.
