import type { BananaRequest } from "./bananaTypes";

const BLOCKED = [
  "nude child",
  "sexual minor",
  "non-consensual",
  "deepfake real person",
  "stolen logo",
  "fake medical result",
  "illegal weapon"
];

export function validateBananaSafety(req: BananaRequest) {
  const text = `${req.prompt} ${req.negativePrompt ?? ""}`.toLowerCase();
  const hit = BLOCKED.find((term) => text.includes(term));
  if (hit) {
    throw new Error(`Google Banana provider safety rejected prompt: ${hit}`);
  }
  if (req.safety?.preserveBrandAssets && req.mode !== "generate" && req.images.length === 0) {
    throw new Error("Brand/object preserving edit requires at least one reference image.");
  }
  return true;
}
