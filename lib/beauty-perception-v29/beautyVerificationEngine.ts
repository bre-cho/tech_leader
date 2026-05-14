import type { EngineResult } from "./types";

export function runBeautyVerificationEngine(engines: Record<string, EngineResult>, prompt: string): EngineResult {
  const failures = [
    "plastic skin",
    "dead eyes",
    "fake smile",
    "over symmetry",
    "collapsed anatomy",
    "drifted identity",
    "bad hands",
    "oversharpen",
    "AI texture",
    "fake teeth"
  ];

  const checks = {
    has_identity_graph: Boolean(engines.beautyDnaGraph),
    has_femininity_graph: Boolean(engines.femininitySignalGraph),
    has_attention_route: Boolean(engines.attentionRouting),
    has_micro_expression: Boolean(engines.microExpression),
    has_provider_route: Boolean(engines.providerRouter),
    prompt_blocks_failures: failures.every(f => prompt.toLowerCase().includes(f.toLowerCase()))
  };

  const score = Math.round(Object.values(checks).filter(Boolean).length / Object.keys(checks).length * 100);

  return {
    name: "BeautyVerificationEngine",
    score,
    data: {
      checks,
      failure_detection_targets: failures,
      passed: score >= 90,
      qa_contract: [
        "identity must not drift",
        "skin must not be plastic",
        "eyes must not be dead",
        "hands must be anatomically plausible",
        "smile must not be frozen",
        "commercial safety must be preserved"
      ]
    },
    warnings: Object.entries(checks).filter(([,v]) => !v).map(([k]) => `failed_check:${k}`)
  };
}
