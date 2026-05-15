import { randomUUID } from "node:crypto";

import { defaultDesignBusinessInput, runBrandBrain } from "@/lib/ai-design-workforce/brand-brain";
import { getAgentRegistryRecord } from "@/lib/ai-design-workforce/agent-registry";
import { recordRuntimeMetric } from "@/lib/ai-design-workforce/runtime-metrics";
import { brandMemoryService, inferDecision } from "@/lib/brand-memory";
import type { AgentRuntimeRequest, AgentRuntimeResult } from "@/lib/ai-design-workforce/types";

const RUNTIME_VERSION = "v17.runtime.1";

function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error(`Agent execution timeout after ${timeoutMs}ms`)), timeoutMs);
    promise
      .then((result) => {
        clearTimeout(timeout);
        resolve(result);
      })
      .catch((error) => {
        clearTimeout(timeout);
        reject(error);
      });
  });
}

function asString(input: Record<string, unknown>, key: string, fallback: string): string {
  const value = input[key];
  return typeof value === "string" && value.trim() ? value : fallback;
}

async function dispatchTask(request: AgentRuntimeRequest): Promise<Record<string, unknown>> {
  const input = request.input || {};
  switch (request.taskType) {
    case "brand_strategy": {
      const brain = runBrandBrain({
        ...defaultDesignBusinessInput,
        niche: asString(input, "niche", defaultDesignBusinessInput.niche),
        targetAudience: asString(input, "targetAudience", defaultDesignBusinessInput.targetAudience),
        corePromise: asString(input, "corePromise", defaultDesignBusinessInput.corePromise),
      });
      return {
        positioning: brain.positioning,
        oneLiner: brain.oneLiner,
        contentPillars: brain.contentPillars,
      };
    }

    case "design_research": {
      const niche = asString(input, "niche", "AI design for growth teams");
      const platform = asString(input, "platform", "TikTok");
      return {
        trendAngles: [
          `Case-study teardown cho niche ${niche}`,
          `Prompt-to-result demo cho ${platform}`,
          "Before/after carousel with conversion overlay",
        ],
        risks: [
          "Visual dep roi vao dep nhung khong ro product",
          "CTA mo ho dan den click-thru thap",
        ],
      };
    }

    case "poster_direction": {
      const product = asString(input, "product", "AI Poster Prompt Pack");
      const audience = asString(input, "audience", "SME founders");
      const goal = asString(input, "goal", "conversion");
      return {
        headline: `Dung bo qua ${product} neu ban muon ra visual co don`,
        cta: "Nhan bo prompt va dung ngay hom nay",
        layout: "product-first editorial asymmetry",
        trustCues: ["social-proof", "clear-value-icons", "readable-price-anchoring"],
        rationale: `Huong toi ${audience} voi muc tieu ${goal} theo nguyen tac hierarchy -> trust -> CTA gravity`,
      };
    }

    case "content_generation": {
      const topic = asString(input, "topic", "AI poster workflow");
      const audience = asString(input, "audience", "business owners");
      return {
        hooks: [
          `Sai lam khien ${audience} lam ${topic} ma khong ra don`,
          `Tu anh thuong thanh poster ban hang trong 15 phut`,
          "Template nao de clone winner nhanh nhat?",
        ],
        scriptOutline: ["Hook 0-3s", "Proof 3-15s", "Framework 15-30s", "CTA 30-40s"],
        cta: "Nhan free checklist va chay thu workflow ngay",
      };
    }

    case "offer_packaging": {
      const winningAngle = asString(input, "winningAngle", "AI poster conversion");
      const priceHint = asString(input, "priceHint", "299k");
      return {
        offerName: `Winner Pack: ${winningAngle}`,
        valueStack: ["50 production prompts", "10 conversion poster templates", "7-day execution sprint"],
        riskReversal: "7-day satisfaction guarantee",
        priceHint,
      };
    }

    case "analytics_review": {
      const ctr = Number(input.ctr || 0);
      const conversionRate = Number(input.conversionRate || 0);
      const cpa = Number(input.cpa || 0);
      const decision = inferDecision(ctr, conversionRate, cpa);
      const isStrong = decision === "clone";

      // Write-back to Brand Memory (V18 hook)
      const brandId = asString(input, "brandId", "default");
      const campaignId = asString(input, "campaignId", `auto_${randomUUID()}`);
      await brandMemoryService.writeCampaign({
        brand_id: brandId,
        campaign: {
          campaign_id: campaignId,
          brand_id: brandId,
          agent_id: request.agentId,
          task_type: request.taskType,
          input_snapshot: input,
          output_snapshot: { decision, ctr, conversionRate, cpa },
          ctr,
          conversion_rate: conversionRate,
          cpa,
          decision,
          hooks: [],
        },
      });

      return {
        decision,
        brand_memory_written: true,
        reasons: isStrong
          ? ["CTR and conversion pass threshold", "CPA in acceptable band"]
          : ["Need stronger hook or CTA", "Optimize offer-message fit before scaling"],
        nextExperiment: isStrong
          ? "Scale to adjacent audience segment with same creative DNA"
          : "Run 3 new hooks with clearer product-value hierarchy",
      };
    }

    default:
      throw new Error(`Unsupported task type: ${request.taskType}`);
  }
}

export async function runAgentTask(request: AgentRuntimeRequest): Promise<AgentRuntimeResult> {
  const startedAt = Date.now();
  const runId = `awr_${randomUUID()}`;

  const finalize = (result: AgentRuntimeResult): AgentRuntimeResult => {
    recordRuntimeMetric(result);
    return result;
  };

  const agent = getAgentRegistryRecord(request.agentId);
  const timeoutMs = Math.max(300, Number(request.policy?.timeoutMs || agent?.defaultPolicy?.timeoutMs || 2500));
  const maxRetries = Math.max(0, Number(request.policy?.maxRetries || agent?.defaultPolicy?.maxRetries || 1));
  if (!agent) {
    return finalize({
      run_id: runId,
      runtime_version: RUNTIME_VERSION,
      agent_id: request.agentId,
      task_type: request.taskType,
      status: "failed",
      attempts: 0,
      latency_ms: Date.now() - startedAt,
      output: null,
      error: `Unknown agentId: ${request.agentId}`,
      diagnostics: {
        timestamp: new Date().toISOString(),
        timeout_ms: timeoutMs,
        max_retries: maxRetries,
      },
    });
  }

  const supportsTask = agent.capabilities.some((capability) => capability.taskType === request.taskType);
  if (!supportsTask) {
    return finalize({
      run_id: runId,
      runtime_version: RUNTIME_VERSION,
      agent_id: request.agentId,
      task_type: request.taskType,
      status: "failed",
      attempts: 0,
      latency_ms: Date.now() - startedAt,
      output: null,
      error: `Agent ${request.agentId} does not support task type ${request.taskType}`,
      diagnostics: {
        timestamp: new Date().toISOString(),
        timeout_ms: timeoutMs,
        max_retries: maxRetries,
      },
    });
  }

  let attempts = 0;
  let lastError: unknown;

  while (attempts <= maxRetries) {
    attempts += 1;
    try {
      const output = await withTimeout(dispatchTask(request), timeoutMs);
      return finalize({
        run_id: runId,
        runtime_version: RUNTIME_VERSION,
        agent_id: request.agentId,
        task_type: request.taskType,
        status: "success",
        attempts,
        latency_ms: Date.now() - startedAt,
        output,
        diagnostics: {
          timestamp: new Date().toISOString(),
          timeout_ms: timeoutMs,
          max_retries: maxRetries,
        },
      });
    } catch (error: unknown) {
      lastError = error;
    }
  }

  return finalize({
    run_id: runId,
    runtime_version: RUNTIME_VERSION,
    agent_id: request.agentId,
    task_type: request.taskType,
    status: "failed",
    attempts,
    latency_ms: Date.now() - startedAt,
    output: null,
    error: lastError instanceof Error ? lastError.message : "Agent task failed",
    diagnostics: {
      timestamp: new Date().toISOString(),
      timeout_ms: timeoutMs,
      max_retries: maxRetries,
    },
  });
}
