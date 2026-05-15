export type RevenueStage = "free" | "low_ticket" | "mid_ticket" | "high_ticket" | "recurring";

export type DesignBusinessInput = {
  founderName?: string;
  brandName?: string;
  niche: string;
  targetAudience: string;
  corePromise: string;
  productCategory: string;
  primaryPlatform: "TikTok" | "Facebook" | "YouTube" | "Instagram" | "Website" | string;
  visualStyle?: string;
  currentOffer?: string;
  pricePoint?: string;
  monthlyRevenueGoal?: string;
};

export type ContextEntity = {
  id: string;
  type: "brand" | "audience" | "offer" | "style" | "content" | "workflow" | "metric" | "memory" | "product";
  name: string;
  summary: string;
  metadata: Record<string, string | number | boolean | string[]>;
};

export type ContextRelation = {
  from: string;
  to: string;
  relation: string;
  weight: number;
};

export type DesignContextGraph = {
  entities: ContextEntity[];
  relations: ContextRelation[];
};

export type AIEmployee = {
  id: string;
  name: string;
  department: string;
  mission: string;
  kpi: string;
  tools: string[];
  outputs: string[];
};

export type WorkflowStep = {
  id: string;
  name: string;
  ownerAgent: string;
  input: string;
  output: string;
  qualityGate: string;
  automationHook?: string;
};

export type BrandBrainOutput = {
  positioning: string;
  oneLiner: string;
  contentPillars: string[];
  productLadder: Array<{ stage: RevenueStage; product: string; promise: string; priceHint: string }>;
  aiEmployees: AIEmployee[];
  contextGraph: DesignContextGraph;
  workflows: Array<{ id: string; name: string; goal: string; steps: WorkflowStep[] }>;
  launchPlan7Days: Array<{ day: number; action: string; artifact: string; successMetric: string }>;
  revenueLoop: string[];
  qualityGates: string[];
};

export type AgentTaskType =
  | "brand_strategy"
  | "design_research"
  | "poster_direction"
  | "content_generation"
  | "offer_packaging"
  | "analytics_review";

export type AgentPermission =
  | "read:brand-context"
  | "read:performance-data"
  | "write:content-plan"
  | "write:offer-brief"
  | "write:poster-brief"
  | "write:strategy";

export interface AgentCapability {
  taskType: AgentTaskType;
  description: string;
  inputSchema: Record<string, string>;
  outputSchema: Record<string, string>;
}

export interface AgentRegistryRecord {
  id: string;
  name: string;
  role: string;
  version: string;
  department: string;
  mission: string;
  permissions: AgentPermission[];
  capabilities: AgentCapability[];
  reliabilityTarget: {
    successRate: number;
    p95LatencyMs: number;
  };
  defaultPolicy?: {
    timeoutMs: number;
    maxRetries: number;
  };
}

export interface AgentRuntimeRequest {
  agentId: string;
  taskType: AgentTaskType;
  input: Record<string, unknown>;
  context?: Record<string, unknown>;
  policy?: {
    timeoutMs?: number;
    maxRetries?: number;
  };
}

export interface AgentRuntimeResult {
  run_id: string;
  runtime_version: string;
  agent_id: string;
  task_type: AgentTaskType;
  status: "success" | "failed";
  attempts: number;
  latency_ms: number;
  output: Record<string, unknown> | null;
  error?: string;
  diagnostics: {
    timestamp: string;
    timeout_ms: number;
    max_retries: number;
  };
}

export interface RuntimeManagerContract {
  runtime_version: string;
  registry_version: string;
  generated_at: string;
  filters: {
    taskType: AgentTaskType | null;
  };
  policies: {
    timeout_ms_min: number;
    timeout_ms_max: number;
    max_retries_max: number;
  };
  tasks: AgentTaskType[];
  total_agents: number;
  agents: AgentRegistryRecord[];
}
