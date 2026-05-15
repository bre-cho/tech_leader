import { randomUUID } from "node:crypto";
import type { PosterProductionInput } from "@/lib/code-intelligence/types";
import { getPosterCodeIntelligenceGraph } from "@/lib/code-intelligence/loader";
import { AutoFixPosterAI, PosterQAAutoCheck } from "@/lib/poster-intelligence/services";
import type { PosterFixPlan, PosterInput as PosterQaInput, QACheckResult } from "@/lib/poster-intelligence/types";
import { AutoIndustryDetector } from "@/lib/scale-intelligence/services";
import type { IndustryDetectResult } from "@/lib/scale-intelligence/types";
import { runAdsFactoryV6Pro } from "@/lib/v6-pro/runtime";
import { runAutoPosterV4 } from "@/lib/v4-poster/engine";
import type { Goal as V4Goal, PosterResponse, VisualVariant } from "@/lib/v4-poster/types";
import { createPosterProductionTrace, type PosterProductionTrace } from "@/lib/poster-production/traces";

type V6ProRun = Awaited<ReturnType<typeof runAdsFactoryV6Pro>>;

export interface PosterProductionRun {
  pipeline_version: "poster-production.cig.v1";
  status: "render_ready" | "fix_required" | "blocked";
  input: NormalizedPosterProductionInput;
  semantic_graph: Awaited<ReturnType<typeof getPosterCodeIntelligenceGraph>>;
  stages: {
    stage_01_code_intelligence_graph: {
      purpose: string;
      node_count: number;
      edge_count: number;
    };
    stage_02_industry_routing: IndustryDetectResult;
    stage_03_v6pro_campaign_reasoning: V6ProRun;
    stage_04_v4_poster_variants: PosterResponse;
    stage_05_quality_gate: QACheckResult;
    stage_06_autofix_if_needed: PosterFixPlan | null;
  };
  winner: VisualVariant | V6ProRun["winner"];
  render_contract: {
    mode: "provider_ready" | "blocked";
    provider_hint: "mock" | "adobe" | "canva" | "adobe+canva";
    prompt?: string;
    negative_prompt?: string;
    required_before_publish: string[];
  };
  trace: PosterProductionTrace;
  agent_next_actions: string[];
}

type NormalizedPosterProductionInput = PosterProductionInput & {
  product: string;
  product_type: string;
  brand: string;
  industry: string;
  audience: string;
  goal: NonNullable<PosterProductionInput["goal"]>;
  platform: string;
  ratio: string;
  value_icons: string[];
};

function normalizeInput(input: PosterProductionInput): NormalizedPosterProductionInput {
  const product = input.product || input.product_type || input.text || "poster product";

  return {
    ...input,
    product,
    product_type: input.product_type || product,
    brand: input.brand || "Brand",
    industry: input.industry || "custom",
    audience: input.audience || "target audience",
    goal: input.goal || "conversion",
    platform: input.platform || "social ads",
    ratio: input.ratio || "4:5",
    value_icons: input.value_icons || ["Lợi ích chính", "Tin cậy", "Hành động nhanh"],
  };
}

function mapGoalToV4(goal: NormalizedPosterProductionInput["goal"]): V4Goal {
  switch (goal) {
    case "conversion":
      return "conversion";
    case "sale":
      return "sale";
    case "education":
      return "trust";
    case "event":
      return "viral";
    case "click":
    case "lead":
    default:
      return "sale";
  }
}

function toQaInput(input: NormalizedPosterProductionInput, winner: VisualVariant): PosterQaInput {
  return {
    poster_id: randomUUID(),
    industry: input.industry,
    brand_name: input.brand,
    headline: input.headline || winner.label || `Khám phá ${input.product}`,
    slogan_or_cta: input.cta || "Inbox ngay",
    value_icons: input.value_icons,
    product_focus: input.product,
    visual_description: winner.prompt,
    metadata: {
      ratio: input.ratio,
      platform: input.platform,
      visual_direction: winner.visualDirection,
      layout: winner.layout,
      perception_targets: input.perception_targets || [],
    },
    colors: [],
    text_blocks: [],
  };
}

export async function runPosterProductionPipeline(input: PosterProductionInput): Promise<PosterProductionRun> {
  const normalized = normalizeInput(input);
  const semanticGraph = await getPosterCodeIntelligenceGraph();

  const industry = new AutoIndustryDetector().detect({
    text: [normalized.text, normalized.product, normalized.industry, normalized.audience]
      .filter(Boolean)
      .join(" "),
    product_name: normalized.product,
    image_description: normalized.text || "",
    metadata: {},
  });

  const enrichedInput: NormalizedPosterProductionInput = {
    ...normalized,
    industry: normalized.industry === "custom" ? industry.industry : normalized.industry,
  };

  const v6pro = await runAdsFactoryV6Pro({
    product_type: enrichedInput.product_type,
    product_info: enrichedInput.text,
    description: enrichedInput.text,
    goal: enrichedInput.goal,
    brand: enrichedInput.brand,
    brand_name: enrichedInput.brand,
    ratio: enrichedInput.ratio,
    platform: enrichedInput.platform,
    cta: enrichedInput.cta,
  });

  const v4 = runAutoPosterV4({
    industry: enrichedInput.industry,
    productName: enrichedInput.product,
    productType: enrichedInput.product_type,
    description: enrichedInput.text,
    goal: mapGoalToV4(enrichedInput.goal),
    target: enrichedInput.audience,
    ingredients: [],
    headline: enrichedInput.headline,
    hasModel: false,
    hasPackaging: enrichedInput.hasPackaging !== false,
    hasCollection: !!enrichedInput.hasCollection,
    useReferenceImage: !!enrichedInput.useReferenceImage,
  });

  const winner = v4.winner;
  const qaInput = toQaInput(enrichedInput, winner);
  const qa = new PosterQAAutoCheck().check(qaInput);
  const autofix = qa.pass_qa ? null : new AutoFixPosterAI().fix(qaInput);
  const status: PosterProductionRun["status"] = qa.pass_qa
    ? "render_ready"
    : qa.decision === "reject"
      ? "blocked"
      : "fix_required";

  const partialRun: Omit<PosterProductionRun, "trace"> = {
    pipeline_version: "poster-production.cig.v1",
    status,
    input: enrichedInput,
    semantic_graph: semanticGraph,
    stages: {
      stage_01_code_intelligence_graph: {
        purpose: semanticGraph.purpose,
        node_count: semanticGraph.nodes.length,
        edge_count: semanticGraph.edges.length,
      },
      stage_02_industry_routing: industry,
      stage_03_v6pro_campaign_reasoning: v6pro,
      stage_04_v4_poster_variants: v4,
      stage_05_quality_gate: qa,
      stage_06_autofix_if_needed: autofix,
    },
    winner,
    render_contract: {
      mode: qa.pass_qa ? "provider_ready" : "blocked",
      provider_hint: "adobe+canva",
      prompt: qa.pass_qa ? winner.prompt : undefined,
      negative_prompt: qa.pass_qa ? winner.negativePrompt : undefined,
      required_before_publish: qa.pass_qa
        ? [
            "Render image with provider",
            "Manual text readability check",
            "Save winner DNA after performance data",
          ]
        : ["Apply AutoFixPosterAI patches", "Regenerate variants", "Run QA again"],
    },
    agent_next_actions: qa.pass_qa
      ? [
          "Send render_contract.prompt to provider",
          "Store output artifact",
          "Track CTR/lead/ROAS",
          "Feed winner DNA learner",
        ]
      : ["Apply autofix", "Re-run /api/poster-production/run", "Do not publish until QA passes"],
  };

  const trace = await createPosterProductionTrace(enrichedInput, partialRun);

  return {
    ...partialRun,
    trace,
  } as PosterProductionRun;
}
