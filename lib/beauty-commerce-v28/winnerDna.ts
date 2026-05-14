import fs from "node:fs";
import path from "node:path";
import type { BeautyCommerceInput } from "./types";

const MEMORY_PATH = path.join(process.cwd(), "storage", "winner-dna", "beauty-commerce-v28-2-v28-3.jsonl");

export function buildWinnerDna(input: BeautyCommerceInput, result: any) {
  return {
    dna_id: `beauty_video_dna_${Date.now()}`,
    brand: input.brandName,
    product: input.productName,
    industry: input.industry,
    channel: input.channel,
    attention_route: result.femininityEngine.beautyAttentionRouting.data.route,
    eye_contact_sequence: result.femininityEngine.eyeContact.data.sequence,
    micro_expression: result.videoEngine.microExpression.data,
    body_language: result.videoEngine.bodyLanguage.data.motionPattern,
    product_attention: result.videoEngine.productAttention.data,
    provider_route: result.providerRoute,
    commercial_score: result.commercialScore,
    prompt: result.prompt,
    video_plan: result.videoPlan,
    created_at: new Date().toISOString()
  };
}

export function saveWinnerDna(dna: Record<string, unknown>) {
  fs.mkdirSync(path.dirname(MEMORY_PATH), { recursive: true });
  fs.appendFileSync(MEMORY_PATH, JSON.stringify(dna) + "\n", "utf8");
  return { saved: true, path: MEMORY_PATH };
}
