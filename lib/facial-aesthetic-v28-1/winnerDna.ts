import fs from "node:fs";
import path from "node:path";
import type { FacialAestheticRequest, FacialAestheticOutput } from "./types";

const MEMORY_PATH = path.join(process.cwd(), "storage", "winner-dna", "facial-aesthetic.jsonl");

export function buildFacialAestheticWinnerDna(req: FacialAestheticRequest, output: FacialAestheticOutput) {
  return {
    dna_id: `facial_dna_${Date.now()}`,
    brand: req.brandName,
    industry: req.industry,
    face_dna: output.face_dna,
    beauty_scoring: output.luxury_face_scoring,
    prompt_enhancer: output.prompt_enhancer,
    beauty_perception_psychology: output.beauty_perception_psychology,
    created_at: new Date().toISOString()
  };
}

export function saveFacialAestheticWinnerDna(dna: Record<string, unknown>) {
  fs.mkdirSync(path.dirname(MEMORY_PATH), { recursive: true });
  fs.appendFileSync(MEMORY_PATH, JSON.stringify(dna) + "\n", "utf8");
  return { saved: true, path: MEMORY_PATH };
}
