import fs from "node:fs";
import path from "node:path";
import type { BeautyCommerceRequest, BeautyCommerceDecision } from "./beautyCommerceTypes";

const MEMORY_PATH = path.join(process.cwd(), "storage", "winner-dna", "beauty-commerce.jsonl");

export function buildBeautyWinnerDna(req: BeautyCommerceRequest, decision: BeautyCommerceDecision, verification: Record<string, any>) {
  return {
    dna_id: `beauty_dna_${Date.now()}`,
    brand: req.brandName,
    industry: req.industry,
    product: req.productName,
    channel: req.channel,
    provider: (decision.providerRoute as any).provider,
    attention_route: (decision.attentionRouting as any).route,
    pose_goal: req.poseGoal,
    outfit_style: req.outfitStyle,
    predicted_conversion: decision.beautyConversionPrediction,
    commercial_score: decision.luxuryBeautyScoring,
    verification_score: verification.score,
    prompt: decision.prompt,
    created_at: new Date().toISOString()
  };
}

export function saveBeautyWinnerDna(dna: Record<string, unknown>) {
  fs.mkdirSync(path.dirname(MEMORY_PATH), {recursive: true});
  fs.appendFileSync(MEMORY_PATH, JSON.stringify(dna) + "\n", "utf8");
  return {saved: true, path: MEMORY_PATH};
}
