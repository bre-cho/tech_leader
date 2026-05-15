export type CreativeGoal = "conversion" | "brand" | "trust" | "viral" | "luxury" | "authority";

export type CreativeStudioBrief = {
  productName: string;
  productType?: string;
  brandName?: string;
  audience?: string;
  industry?: string;
  platform?: string;
  goal?: CreativeGoal | string;
  offer?: string;
  cta?: string;
  ratio?: string;
  desiredPerception?: string[];
  constraints?: string[];
  referenceNotes?: string;
};

export type PerceptionNode = {
  id: string;
  label: string;
  score: number;
  signals: string[];
  recommendedVisualMoves: string[];
};

export type CIGNode = {
  id: string;
  type:
    | "perception"
    | "branding"
    | "composition"
    | "typography"
    | "emotion"
    | "campaign"
    | "action";
  label: string;
  meaning: string;
  weight: number;
};

export type CIGEdge = {
  from: string;
  to: string;
  relation: "amplifies" | "supports" | "risks" | "constrains" | "evolves";
  reason: string;
};

export type CreativeIntelligenceGraph = {
  graphId: string;
  nodes: CIGNode[];
  edges: CIGEdge[];
  summary: string;
};

export type CreativeAgentName =
  | "PerceptionAgent"
  | "TypographyAgent"
  | "CompositionAgent"
  | "BrandMemoryAgent"
  | "CampaignEvolutionAgent"
  | "QAGateAgent";

export type CreativeAgentDecision = {
  agent: CreativeAgentName;
  decision: string;
  confidence: number;
  actions: string[];
};

export type CreativeOSActionMode =
  | "run_full_pipeline"
  | "generate_variants"
  | "improve_luxury"
  | "increase_trust"
  | "increase_product_dominance"
  | "fix_typography"
  | "fix_qa"
  | "explain_graph"
  | "save_winner";

export type CreativeOSRequest = {
  mode?: CreativeOSActionMode;
  instruction?: string;
  brief: CreativeStudioBrief;
  currentState?: Record<string, unknown>;
  performance?: {
    impressions?: number;
    clicks?: number;
    leads?: number;
    sales?: number;
    spend?: number;
    revenue?: number;
  };
};

export type CreativeOSResponse = {
  ok: boolean;
  mode: CreativeOSActionMode;
  brief: CreativeStudioBrief;
  perception: {
    desired: string[];
    nodes: PerceptionNode[];
    totalScore: number;
  };
  graph: CreativeIntelligenceGraph;
  agentDecisions: CreativeAgentDecision[];
  execution: {
    v6?: unknown;
    v4?: unknown;
    qa?: unknown;
    fixPlan?: unknown;
  };
  winner: unknown;
  renderContract: {
    status: "ready_for_provider" | "needs_fix" | "blocked";
    /** "provider_pending" means the contract is compiled and ready to be sent
     *  to a render provider; no provider has been invoked by this layer yet.
     *  Other values represent a specific provider integration being active. */
    provider: "provider_pending" | "invokeai" | "veo" | "runway" | "kling";
    posterPrompt?: string;
    negativePrompt?: string;
    ratio: string;
    nextProviderPayload: Record<string, unknown>;
  };
  memory: {
    shouldLearn: boolean;
    dna: Record<string, unknown>;
    evolutionHints: string[];
  };
  nextActions: string[];
  createdAt: string;
};
