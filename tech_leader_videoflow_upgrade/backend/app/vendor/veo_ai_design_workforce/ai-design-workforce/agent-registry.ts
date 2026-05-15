import { createDesignEmployees } from "@/lib/ai-design-workforce/brand-brain";
import type { AgentRegistryRecord, AgentTaskType } from "@/lib/ai-design-workforce/types";

const VERSION = "v17.registry.1";

function defaultPolicy(taskType: AgentTaskType) {
  switch (taskType) {
    case "poster_direction":
      return { timeoutMs: 3200, maxRetries: 1 };
    case "analytics_review":
      return { timeoutMs: 2200, maxRetries: 2 };
    default:
      return { timeoutMs: 2500, maxRetries: 1 };
  }
}

function capability(taskType: AgentTaskType, description: string, inputSchema: Record<string, string>, outputSchema: Record<string, string>) {
  return { taskType, description, inputSchema, outputSchema };
}

const REGISTRY: AgentRegistryRecord[] = createDesignEmployees().map((employee) => {
  switch (employee.id) {
    case "brand-strategy-agent":
      return {
        id: employee.id,
        name: employee.name,
        role: "Brand Strategist",
        version: VERSION,
        department: employee.department,
        mission: employee.mission,
        permissions: ["read:brand-context", "write:strategy"],
        capabilities: [
          capability(
            "brand_strategy",
            "Synthesizes positioning, one-liner, and content pillars from business context.",
            { niche: "string", targetAudience: "string", corePromise: "string" },
            { positioning: "string", oneLiner: "string", contentPillars: "string[]" }
          ),
        ],
        reliabilityTarget: { successRate: 0.98, p95LatencyMs: 1200 },
        defaultPolicy: defaultPolicy("brand_strategy"),
      };
    case "design-research-agent":
      return {
        id: employee.id,
        name: employee.name,
        role: "Design Researcher",
        version: VERSION,
        department: employee.department,
        mission: employee.mission,
        permissions: ["read:brand-context", "write:content-plan"],
        capabilities: [
          capability(
            "design_research",
            "Builds trend angles and visual opportunities for a niche.",
            { niche: "string", platform: "string" },
            { trendAngles: "string[]", risks: "string[]" }
          ),
        ],
        reliabilityTarget: { successRate: 0.96, p95LatencyMs: 1500 },
        defaultPolicy: defaultPolicy("design_research"),
      };
    case "poster-director-agent":
      return {
        id: employee.id,
        name: employee.name,
        role: "Poster Director",
        version: VERSION,
        department: employee.department,
        mission: employee.mission,
        permissions: ["read:brand-context", "write:poster-brief"],
        capabilities: [
          capability(
            "poster_direction",
            "Creates poster brief with hierarchy, CTA gravity, and trust cues.",
            { product: "string", audience: "string", goal: "string" },
            { headline: "string", cta: "string", layout: "string", trustCues: "string[]" }
          ),
        ],
        reliabilityTarget: { successRate: 0.95, p95LatencyMs: 1800 },
        defaultPolicy: defaultPolicy("poster_direction"),
      };
    case "content-agent":
      return {
        id: employee.id,
        name: employee.name,
        role: "Content Producer",
        version: VERSION,
        department: employee.department,
        mission: employee.mission,
        permissions: ["read:brand-context", "write:content-plan"],
        capabilities: [
          capability(
            "content_generation",
            "Generates hooks, script skeletons, and CTA blocks.",
            { topic: "string", audience: "string", platform: "string" },
            { hooks: "string[]", scriptOutline: "string[]", cta: "string" }
          ),
        ],
        reliabilityTarget: { successRate: 0.96, p95LatencyMs: 1200 },
        defaultPolicy: defaultPolicy("content_generation"),
      };
    case "offer-agent":
      return {
        id: employee.id,
        name: employee.name,
        role: "Offer Architect",
        version: VERSION,
        department: employee.department,
        mission: employee.mission,
        permissions: ["read:brand-context", "write:offer-brief"],
        capabilities: [
          capability(
            "offer_packaging",
            "Packages low-ticket and mid-ticket offers from a winning angle.",
            { winningAngle: "string", priceHint: "string" },
            { offerName: "string", valueStack: "string[]", riskReversal: "string" }
          ),
        ],
        reliabilityTarget: { successRate: 0.95, p95LatencyMs: 1400 },
        defaultPolicy: defaultPolicy("offer_packaging"),
      };
    default:
      return {
        id: employee.id,
        name: employee.name,
        role: "Analytics Operator",
        version: VERSION,
        department: employee.department,
        mission: employee.mission,
        permissions: ["read:performance-data", "read:brand-context", "write:strategy"],
        capabilities: [
          capability(
            "analytics_review",
            "Evaluates campaign performance and returns clone/improve/kill decision.",
            { ctr: "number", conversionRate: "number", cpa: "number" },
            { decision: "string", reasons: "string[]", nextExperiment: "string" }
          ),
        ],
        reliabilityTarget: { successRate: 0.97, p95LatencyMs: 1100 },
        defaultPolicy: defaultPolicy("analytics_review"),
      };
  }
});

export function listAgentRegistry(): AgentRegistryRecord[] {
  return REGISTRY;
}

export function getAgentRegistryRecord(agentId: string): AgentRegistryRecord | undefined {
  return REGISTRY.find((agent) => agent.id === agentId);
}

export function listAgentRegistryByTaskType(taskType?: AgentTaskType): AgentRegistryRecord[] {
  if (!taskType) {
    return REGISTRY;
  }
  return REGISTRY.filter((agent) => agent.capabilities.some((capability) => capability.taskType === taskType));
}

export function listSupportedTaskTypes(): AgentTaskType[] {
  const set = new Set<AgentTaskType>();
  for (const agent of REGISTRY) {
    for (const capability of agent.capabilities) {
      set.add(capability.taskType);
    }
  }
  return Array.from(set.values());
}
