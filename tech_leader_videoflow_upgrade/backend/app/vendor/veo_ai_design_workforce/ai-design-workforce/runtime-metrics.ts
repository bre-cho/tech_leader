import type { AgentRuntimeResult } from "@/lib/ai-design-workforce/types";

type RuntimeMetricEvent = {
  runId: string;
  agentId: string;
  taskType: string;
  status: "success" | "failed";
  latencyMs: number;
  error: string | null;
  at: string;
};

type RuntimeMetricsStore = {
  events: RuntimeMetricEvent[];
};

const MAX_EVENTS = 1000;

function getStore(): RuntimeMetricsStore {
  const globalStore = globalThis as typeof globalThis & {
    __aiWorkforceRuntimeMetrics?: RuntimeMetricsStore;
  };

  if (!globalStore.__aiWorkforceRuntimeMetrics) {
    globalStore.__aiWorkforceRuntimeMetrics = { events: [] };
  }

  return globalStore.__aiWorkforceRuntimeMetrics;
}

function percentile(values: number[], p: number): number {
  if (values.length === 0) {
    return 0;
  }

  const sorted = [...values].sort((a, b) => a - b);
  const index = Math.min(sorted.length - 1, Math.ceil((p / 100) * sorted.length) - 1);
  return sorted[index];
}

export function recordRuntimeMetric(result: AgentRuntimeResult) {
  const store = getStore();
  store.events.push({
    runId: result.run_id,
    agentId: result.agent_id,
    taskType: result.task_type,
    status: result.status,
    latencyMs: result.latency_ms,
    error: result.error || null,
    at: result.diagnostics.timestamp,
  });

  if (store.events.length > MAX_EVENTS) {
    store.events.splice(0, store.events.length - MAX_EVENTS);
  }
}

export type TrendPoint = {
  index: number;
  latency_ms: number;
  success: boolean;
  at: string;
};

export type RuntimeMetricsFilter = {
  agentId?: string;
  taskType?: string;
  trendLimit?: number;
};

export function getRuntimeMetrics(filter: RuntimeMetricsFilter | string = {}) {
  // backward-compat: callers that pass a raw string agentId keep working
  const resolved: RuntimeMetricsFilter =
    typeof filter === "string" ? { agentId: filter } : filter;

  const store = getStore();
  let events = store.events;

  if (resolved.agentId) {
    events = events.filter((e) => e.agentId === resolved.agentId);
  }
  if (resolved.taskType) {
    events = events.filter((e) => e.taskType === resolved.taskType);
  }

  const byAgent = new Map<
    string,
    {
      totalRuns: number;
      successRuns: number;
      failedRuns: number;
      latencies: number[];
      failureReasons: Record<string, number>;
    }
  >();

  for (const event of events) {
    const current = byAgent.get(event.agentId) ?? {
      totalRuns: 0,
      successRuns: 0,
      failedRuns: 0,
      latencies: [],
      failureReasons: {},
    };

    current.totalRuns += 1;
    current.latencies.push(event.latencyMs);

    if (event.status === "success") {
      current.successRuns += 1;
    } else {
      current.failedRuns += 1;
      const reason = event.error || "unknown";
      current.failureReasons[reason] = (current.failureReasons[reason] || 0) + 1;
    }

    byAgent.set(event.agentId, current);
  }

  const agents = [...byAgent.entries()].map(([id, value]) => ({
    agent_id: id,
    total_runs: value.totalRuns,
    success_rate: value.totalRuns === 0 ? 0 : Number((value.successRuns / value.totalRuns).toFixed(4)),
    p95_latency_ms: percentile(value.latencies, 95),
    failure_reasons: value.failureReasons,
  }));

  const allLatencies = events.map((event) => event.latencyMs);
  const totalRuns = events.length;
  const successRuns = events.filter((event) => event.status === "success").length;

  // trend: last N events ordered by time for chart display
  const trendLimit = Math.max(5, Math.min(50, resolved.trendLimit ?? 20));
  const trendEvents = events.slice(-trendLimit);
  const trend: TrendPoint[] = trendEvents.map((event, index) => ({
    index,
    latency_ms: event.latencyMs,
    success: event.status === "success",
    at: event.at,
  }));

  return {
    runtime_metrics_version: "v17.runtime.metrics.1",
    generated_at: new Date().toISOString(),
    filters: {
      agentId: resolved.agentId ?? null,
      taskType: resolved.taskType ?? null,
    },
    total_runs: totalRuns,
    success_rate: totalRuns === 0 ? 0 : Number((successRuns / totalRuns).toFixed(4)),
    p95_latency_ms: percentile(allLatencies, 95),
    agents,
    trend,
  };
}
