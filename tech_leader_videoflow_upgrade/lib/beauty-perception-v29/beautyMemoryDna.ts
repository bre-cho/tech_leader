import path from "node:path";
import { appendJsonl } from "@/lib/runtime/artifactStore";
import type { BeautyPerceptionRequest, BeautyPerceptionOutput } from "./types";

const MEMORY_PATH = path.join(process.cwd(), "storage", "winner-dna", "v29-beauty-perception.jsonl");

export function buildBeautyMemoryDna(req: BeautyPerceptionRequest, output: Omit<BeautyPerceptionOutput, "memoryDna">) {
  return {
    winner_id: `beauty_${req.lightingStyle.toLowerCase()}_${Date.now()}`,
    brand: req.brandName,
    campaign: req.campaignName,
    platform: req.platform,
    eye_contact: output.engines.eyeContact.score,
    warmth: output.engines.lightingGraph.score,
    femininity: output.engines.femininitySignalGraph.score,
    luxury: output.engines.lightingGraph.score,
    intimacy: output.engines.handToFace.score,
    ctr_prediction: output.socialCtrPrediction.score,
    beauty_score: output.commercialBeautyScore,
    scene_spec: output.sceneSpec,
    provider_route: output.providerRoute,
    created_at: new Date().toISOString()
  };
}

export function saveBeautyMemoryDna(dna: Record<string, unknown>) {
  appendJsonl(MEMORY_PATH, dna);
  return { saved: true, path: MEMORY_PATH };
}
