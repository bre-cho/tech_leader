import { randomUUID } from "node:crypto";
import { runAutoPosterV4 } from "@/lib/v4-poster/engine";
import { runAdsFactoryV6Pro } from "@/lib/v6-pro/runtime";
import { AutoFixPosterAI, PosterQAAutoCheck } from "@/lib/poster-intelligence";
import { buildCreativeIntelligenceGraph } from "@/lib/creative-os/creative-semantic-graph";
import { buildPerceptionNodes, summarizePerception } from "@/lib/creative-os/perception-engine";
import type { CreativeAgentDecision, CreativeOSRequest, CreativeOSResponse } from "@/lib/creative-os/types";

function modeInstruction(mode: string, instruction = "") {
  const map: Record<string, string> = {
    improve_luxury: "Increase luxury perception: more whitespace, restrained palette, editorial serif hierarchy, isolated product hero.",
    increase_trust: "Increase trust: clearer proof block, cleaner hierarchy, product clarity, expert cue.",
    increase_product_dominance: "Increase product dominance: enlarge hero product, reduce secondary clutter, sharpen first fixation.",
    fix_typography: "Fix typography hierarchy: shorten headline, separate CTA gravity, reduce competing text blocks.",
    fix_qa: "Run QA autofix and return corrected render contract.",
    explain_graph: "Explain why each creative node exists and what it controls.",
    save_winner: "Prepare winner DNA for memory/evolution.",
    generate_variants: "Generate multiple creative variants and pick the highest-scoring candidate.",
    run_full_pipeline: "Run the full closed-loop poster production pipeline."
  };
  return [map[mode] || map.run_full_pipeline, instruction].filter(Boolean).join(" ");
}

function buildAgentDecisions(mode: string, perceptionTotal: number): CreativeAgentDecision[] {
  return [
    {
      agent: "PerceptionAgent",
      decision: perceptionTotal >= 80 ? "Perception intent is strong enough for execution." : "Perception needs sharper positioning.",
      confidence: perceptionTotal,
      actions: ["Map desired perception to color, light, spacing, and hierarchy", "Reject random visual decoration"]
    },
    {
      agent: "TypographyAgent",
      decision: mode === "fix_typography" ? "Prioritize headline compression and CTA gravity." : "Keep typography subordinate to product and perception.",
      confidence: 84,
      actions: ["Headline = attention dominance node", "CTA = conversion gravity node"]
    },
    {
      agent: "CompositionAgent",
      decision: mode === "increase_product_dominance" ? "Push product hero to first fixation." : "Use visual tension without clutter.",
      confidence: 86,
      actions: ["Create clear product isolation", "Balance proof, hook, and CTA zones"]
    },
    {
      agent: "BrandMemoryAgent",
      decision: "Store the winning semantic pattern, not just the prompt.",
      confidence: 82,
      actions: ["Capture perception tokens", "Capture typography/composition winner traits"]
    },
    {
      agent: "CampaignEvolutionAgent",
      decision: "Recommend next test based on weakest score dimension.",
      confidence: 80,
      actions: ["Clone winner only after QA", "Avoid semantic duplicate variants"]
    },
    {
      agent: "QAGateAgent",
      decision: "Block publishing when required poster hardlocks fail.",
      confidence: 90,
      actions: ["Run PosterQAAutoCheck", "Return AutoFix plan if needed"]
    }
  ];
}

function buildPosterQAInput(req: CreativeOSRequest, prompt: string) {
  const brief = req.brief;
  return {
    poster_id: randomUUID(),
    industry: brief.industry || brief.productType || "custom",
    brand_name: brief.brandName,
    headline: brief.offer || brief.productName || "Poster campaign",
    slogan_or_cta: brief.cta || "Inbox nhận tư vấn",
    value_icons: ["Trust", "Premium", "Result"],
    product_focus: brief.productName,
    colors: [],
    text_blocks: [brief.productName, brief.offer, brief.cta].filter(Boolean) as string[],
    visual_description: prompt,
    metadata: { mode: req.mode, platform: brief.platform, ratio: brief.ratio }
  };
}

function pickPrompt(
  v4: { winner?: { prompt?: string } } | null,
  v6: { winner?: { prompt?: string } | null; scored_variants?: Record<string, { prompt?: string }> } | null
): string {
  return (
    v4?.winner?.prompt ||
    v6?.winner?.prompt ||
    Object.values(v6?.scored_variants || {})?.[0]?.["prompt"] ||
    "commercial advertising poster, strong product hero, clear headline, clean CTA, high quality"
  );
}

export async function runCreativeOS(input: CreativeOSRequest): Promise<CreativeOSResponse> {
  const mode = input.mode || "run_full_pipeline";
  const brief = {
    ...input.brief,
    productName: input.brief.productName || "Main product",
    goal: input.brief.goal || "conversion",
    ratio: input.brief.ratio || "4:5",
    platform: input.brief.platform || "Meta/TikTok"
  };
  const instruction = modeInstruction(mode, input.instruction);

  const perceptionNodes = buildPerceptionNodes({ ...brief, desiredPerception: brief.desiredPerception });
  const perception = summarizePerception(perceptionNodes);
  const graph = buildCreativeIntelligenceGraph(brief, perceptionNodes, instruction);

  const v6 = await runAdsFactoryV6Pro({
    product_type: brief.productType || brief.industry,
    product_info: [brief.productName, brief.offer, brief.referenceNotes].filter(Boolean).join(" | "),
    description: input.instruction || brief.referenceNotes,
    goal: String(brief.goal || "conversion"),
    brand: brief.brandName,
    ratio: brief.ratio,
    platform: brief.platform,
    cta: brief.cta,
    emotion: perception.desired.join(", ")
  });

  const v4 = runAutoPosterV4({
    industry: brief.industry || String((v6 as any).industry || "general"),
    productName: brief.productName,
    productType: brief.productType,
    description: [brief.offer, instruction, brief.referenceNotes].filter(Boolean).join(". "),
    goal: String(brief.goal || "conversion") as any,
    mood: perception.desired.join(", "),
    target: brief.audience,
    headline: brief.offer || (v6 as any).winner?.hook,
    subline1: brief.referenceNotes,
    subline2: brief.platform,
    hasPackaging: true
  });

  const prompt = pickPrompt(v4, v6);
  const qaInput = buildPosterQAInput(input, prompt);
  const qa = new PosterQAAutoCheck().check(qaInput);
  const fixPlan = qa.pass_qa ? null : new AutoFixPosterAI().fix(qaInput);
  const agentDecisions = buildAgentDecisions(mode, perception.totalScore);

  const winner = v4.winner || (v6 as any).winner;
  const shouldLearn = qa.pass_qa && Math.max(winner?.scores?.finalScore || 0, (v6 as any).winner?.score?.total || 0) >= 85;
  const status = qa.pass_qa ? "ready_for_provider" : qa.decision === "reject" ? "blocked" : "needs_fix";

  return {
    ok: true,
    mode,
    brief,
    perception,
    graph,
    agentDecisions,
    execution: { v6, v4, qa, fixPlan },
    winner,
    renderContract: {
      status,
      provider: "provider_pending",
      posterPrompt: prompt,
      negativePrompt: v4?.winner?.negativePrompt || "low quality, distorted typography, cropped product, unreadable text",
      ratio: brief.ratio || "4:5",
      nextProviderPayload: {
        prompt,
        negative_prompt: v4?.winner?.negativePrompt,
        width_height_ratio: brief.ratio || "4:5",
        seed_policy: "fixed_seed_for_replayability",
        qa_required: true,
        cig_graph_id: graph.graphId
      }
    },
    memory: {
      shouldLearn,
      dna: {
        brand: brief.brandName || "unbranded",
        product: brief.productName,
        industry: brief.industry || (v6 as any).industry,
        perception_tokens: perception.desired,
        winning_variant: winner?.variant || (winner as any)?.type || "conversion",
        semantic_reason: graph.summary,
        typography_law: "headline = attention dominance; CTA = conversion gravity",
        composition_law: "product isolation + eye-flow control + reduced clutter"
      },
      evolutionHints: [
        ...((v6 as any).next_hints || []),
        ...(qa.pass_qa ? ["QA passed: ready to test as controlled variant."] : ["QA did not pass: apply fixPlan before rendering."])
      ]
    },
    nextActions: [
      qa.pass_qa ? "Render poster with provider" : "Apply QA autofix first",
      "Compare authority/viral/conversion variants",
      shouldLearn ? "Save winner DNA to Brand Memory" : "Run one more iteration before learning",
      "Create short video adaptation from winning poster"
    ],
    createdAt: new Date().toISOString()
  };
}
