import path from "node:path";
import { appendJsonl } from "@/lib/runtime/artifactStore";
import type { BeautyIdentityRuntimeRequest, BeautyIdentityRuntimeOutput } from "./types";

const MEMORY_PATH = path.join(process.cwd(), "storage", "winner-dna", "v29-1-identity-lock-beauty.jsonl");

export function buildIdentityWinnerDna(req: BeautyIdentityRuntimeRequest, out: Omit<BeautyIdentityRuntimeOutput, "winnerDna">) {
  return {
    winner_id: `identity_beauty_${req.visualIntent}_${Date.now()}`,
    brand: req.brandName,
    campaign: req.campaignName,
    visual_intent: req.visualIntent,
    platform: req.platform,
    face_lock: out.faceLockContract.data,
    visual_recipe: out.visualRecipe.data,
    provider_route: out.providerRoute.data,
    qa_score: out.qaReport.score,
    prompt_pack: out.promptPack.data,
    created_at: new Date().toISOString()
  };
}

export function saveIdentityWinnerDna(dna: Record<string, unknown>) {
  appendJsonl(MEMORY_PATH, dna);
  return { saved: true, path: MEMORY_PATH };
}
