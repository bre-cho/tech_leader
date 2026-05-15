export type BudgetTier = "low" | "mid" | "premium";

export type DesignStudioRequest = {
  industry: string;
  product: string;
  audience: string;
  channel: string;
  goal: string;
  brand_name: string;
  tone: string;
  budget_tier: BudgetTier;
  language: string;
  dry_run: boolean;
  source_image_data_url?: string;
};

export type ScoreCard = {
  attention_score: number;
  trust_score: number;
  conversion_score: number;
  brand_fit_score: number;
  upsell_video_potential_score: number;
  video_upsell_ready: boolean;
  rationale: string;
};

export type ImageConcept = {
  concept_id: string;
  headline: string;
  cta: string;
  visual_type: string;
  layout_direction: string;
  prompt: string;
  negative_prompt?: string | null;
  mock_image_url?: string | null;
  score?: ScoreCard | null;
  provider_contract?: Record<string, unknown> | null;
  selling_mechanism?: Record<string, unknown> | null;
};

export type OperatingLawTrace = {
  target_define: boolean;
  research: boolean;
  plan: boolean;
  execute: boolean;
  verify: boolean;
  distill_to_skill: boolean;
  memory_update: boolean;
  winner_dna_update: boolean;
};

export type DesignStudioResponse = {
  workflow_id: string;
  dry_run: boolean;
  promotion_mode: "REAL" | "DRY_RUN";
  operating_law: string;
  law_trace: OperatingLawTrace;
  technical_lead_plan: Record<string, unknown>;
  capability_route: Array<Record<string, unknown>>;
  recalled_winner_dna: Array<Record<string, unknown>>;
  business_diagnosis: Record<string, unknown>;
  image_concepts: ImageConcept[];
  best_concept: ImageConcept;
  upsell_analysis: Record<string, unknown>;
  video_concept_preview: Record<string, unknown>;
  storyboard: Array<Record<string, unknown>>;
  offer_packages: Array<Record<string, unknown>>;
  skill_distillation: Record<string, unknown>;
  context_graph_update?: Record<string, unknown> | null;
  memory_update: Record<string, unknown>;
  verification: Record<string, unknown>;
  promotion_gate: Record<string, unknown>;
};

export const defaultDesignBrief: DesignStudioRequest = {
  industry: "Beauty / K-Beauty",
  product: "AI video campaign",
  audience: "Nu 18-34, quan tam lam dep va short video",
  channel: "TikTok / Reels / Shorts",
  goal: "Tang conversion va brand recall",
  brand_name: "TUNGNS Studio",
  tone: "premium, trustworthy, conversion-focused",
  budget_tier: "mid",
  language: "vi",
  dry_run: false,
  source_image_data_url: "",
};

export async function runDesignStudio(payload: DesignStudioRequest): Promise<DesignStudioResponse> {
  const response = await fetch(`/api/v1/design-studio/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Design Studio API failed with status ${response.status}`);
  }

  return (await response.json()) as DesignStudioResponse;
}
