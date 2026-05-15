import type { BeautyCommerceInput, BeautyReference, EngineReport } from "./types";

const REQUIRED = ["identity", "makeup", "fashion", "lighting", "pose"] as const;

function refsOf(kind: string, refs: BeautyReference[]) {
  return refs.filter((r) => r.kind === kind);
}

export function buildBananaMultiReferenceEngine(input: BeautyCommerceInput): EngineReport {
  const locks = REQUIRED.map((kind) => {
    const list = refsOf(kind, input.references);
    return {
      kind,
      available: list.length > 0,
      count: list.length,
      labels: list.map((r) => r.label),
      lockStrength: list.length ? Math.max(...list.map((r) => r.lockStrength)) : 0
    };
  });

  const coverage = locks.filter((l) => l.available).length / REQUIRED.length;
  const score = Math.round(70 + coverage * 30);

  const promptInjection = [
    "Use multi-reference conditioning as locked commercial anchors:",
    ...locks.map((l) => `- ${l.kind}: ${l.available ? `${l.labels.join(", ")}; lock=${l.lockStrength}` : "missing, infer from brand DNA"}`),
    "Preserve identity, makeup, fashion silhouette, lighting mood and pose logic across all generated assets.",
    "Do not change product shape, face identity, makeup DNA, outfit category or commercial layout unless explicitly requested."
  ].join("\n");

  return {
    name: "BananaMultiReferenceEngine",
    score,
    data: {
      requiredReferences: REQUIRED,
      locks,
      coverage,
      promptInjection,
      bananaRole: "default provider for beauty commerce consistency, commercial composition, product layout and TikTok creatives"
    },
    warnings: locks.filter((l) => !l.available).map((l) => `Missing ${l.kind} reference; engine will infer from avatar DNA.`)
  };
}
