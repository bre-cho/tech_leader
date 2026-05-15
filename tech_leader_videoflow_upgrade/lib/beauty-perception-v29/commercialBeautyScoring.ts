import type { EngineResult } from "./types";

export function calculateCommercialBeautyScore(engines: Record<string, EngineResult>) {
  const trust_score = engines.eyeContact.score;
  const femininity_score = engines.femininitySignalGraph.score;
  const luxury_score = engines.lightingGraph.score;
  const intimacy_score = engines.handToFace.score;
  const realism_score = engines.beautyDnaGraph.score;
  const composition_score = engines.attentionRouting.score;

  const beauty_score = Math.round(
    trust_score * 0.25 +
    femininity_score * 0.20 +
    luxury_score * 0.20 +
    intimacy_score * 0.15 +
    realism_score * 0.10 +
    composition_score * 0.10
  );

  return {
    trust_score,
    femininity_score,
    luxury_score,
    intimacy_score,
    realism_score,
    composition_score,
    beauty_score,
    passed: beauty_score >= 90,
    formula: "trust*0.25 + femininity*0.20 + luxury*0.20 + intimacy*0.15 + realism*0.10 + composition*0.10"
  };
}
