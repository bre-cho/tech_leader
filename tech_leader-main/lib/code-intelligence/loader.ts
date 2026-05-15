import type { PosterCodeIntelligenceGraph } from "./types";

export async function getPosterCodeIntelligenceGraph(): Promise<PosterCodeIntelligenceGraph> {
  return {
    purpose: "poster code intelligence graph",
    nodes: [{ id: "root", label: "Root" }],
    edges: [],
  };
}
