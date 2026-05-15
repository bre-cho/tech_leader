import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";

import type { PosterProductionInput } from "@/lib/code-intelligence/types";
import type { PosterProductionRun } from "@/lib/poster-production/orchestrator";
import { log } from "@/lib/logger";
import { observability } from "@/lib/observability";
import { getSupabaseServiceClient } from "@/lib/supabase/server";
import { isProductionLikeRuntime } from "@/lib/config/runtime-guards";

const TRACE_DIR = path.join(process.cwd(), "storage", "poster-production-traces");

/**
 * OPERATIONAL RISK: Traces are written to the local filesystem.
 * In serverless / ephemeral container environments this data is LOST on restart.
 * To make traces durable:
 *   - Write to Supabase (add a poster_production_traces table), OR
 *   - Mount a persistent volume at process.env.POSTER_TRACE_DIR, OR
 *   - Ship traces to an external observability store.
 *
 * Check the environment variable POSTER_TRACE_BACKEND:
 *   "supabase" (default) – durable writes to poster_production_traces table.
 *   "filesystem"         – writes to local storage dir (ephemeral, dev-only).
 *   "disabled"           – skips persistence (trace returned in-memory only).
 *
 * NOTE: "s3" is NOT a supported backend value. If POSTER_TRACE_BACKEND=s3 is
 * configured, this module will log a warning and fall back to "supabase".
 *
 * When running in a production-like environment without a durable backend,
 * this module emits a one-time warning and records a fallback activation metric.
 */
let _traceBackendWarnEmitted = false;
let _filesystemFallbackMetricEmitted = false;

function emitTraceBackendWarning(): void {
  if (_traceBackendWarnEmitted) return;
  _traceBackendWarnEmitted = true;

  if (isProductionLikeRuntime()) {
    log(
      "warn",
      "poster-production/traces",
      "Traces are using a non-durable backend in production-like environment.",
      { traceDir: TRACE_DIR }
    );
  }
}

type TraceBackend = "supabase" | "disabled" | "filesystem";

function resolveTraceBackend(): TraceBackend {
  const raw = String(process.env.POSTER_TRACE_BACKEND || "supabase").trim().toLowerCase();
  if (raw === "s3") {
    // "s3" is not an implemented backend. Warn and fall back to "supabase".
    log(
      "warn",
      "poster-production/traces",
      "POSTER_TRACE_BACKEND=s3 is not implemented. Falling back to 'supabase'. " +
        "Use POSTER_TRACE_BACKEND=supabase, filesystem, or disabled.",
      {}
    );
    return "supabase";
  }
  if (raw === "disabled" || raw === "filesystem" || raw === "supabase") {
    return raw;
  }
  return "supabase";
}

function hasSupabasePersistence(): boolean {
  return !!(
    process.env.NEXT_PUBLIC_SUPABASE_URL &&
    process.env.SUPABASE_SERVICE_ROLE_KEY
  );
}

async function writeSupabaseTrace(trace: PosterProductionTrace): Promise<void> {
  if (!hasSupabasePersistence()) {
    throw new Error(
      "[poster-production/traces] Supabase trace backend requires NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
    );
  }
  const supabase = getSupabaseServiceClient();
  const { error } = await supabase.from("poster_production_traces").insert({
    run_id: trace.run_id,
    input_hash: trace.input_hash,
    created_at: trace.created_at,
    input: trace.input,
    status: trace.status,
    module_trace: trace.module_trace,
    winner_variant_id: trace.winner_variant_id,
    qa_result: trace.qa_result,
    render_artifact_id: trace.render_artifact_id,
    performance_event_id: trace.performance_event_id,
    render_contract: trace.render_contract,
  });
  if (error) {
    throw new Error(`[poster-production/traces] Cannot persist trace: ${error.message}`);
  }
}

async function listSupabaseTraces(limit: number): Promise<PosterProductionTrace[]> {
  if (!hasSupabasePersistence()) {
    if (isProductionLikeRuntime()) {
      throw new Error(
        "[poster-production/traces] Supabase trace backend requires NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
      );
    }
    return [];
  }
  const supabase = getSupabaseServiceClient();
  const { data, error } = await supabase
    .from("poster_production_traces")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(limit);
  if (error) {
    throw new Error(`[poster-production/traces] Cannot load traces: ${error.message}`);
  }
  return (data || []) as PosterProductionTrace[];
}

async function writeFilesystemTrace(trace: PosterProductionTrace): Promise<void> {
  await mkdir(TRACE_DIR, { recursive: true });
  emitTraceBackendWarning();
  if (!_filesystemFallbackMetricEmitted) {
    _filesystemFallbackMetricEmitted = true;
    observability.recordFallbackActivation("poster-production/traces", "filesystem");
  }
  await writeFile(path.join(TRACE_DIR, `${trace.run_id}.json`), JSON.stringify(trace, null, 2), "utf8");
}

async function listFilesystemTraces(limit: number): Promise<PosterProductionTrace[]> {
  await mkdir(TRACE_DIR, { recursive: true });
  const entries = await readdir(TRACE_DIR);
  const traces = await Promise.all(
    entries
      .filter((entry) => entry.endsWith(".json"))
      .slice(-limit)
      .reverse()
      .map(async (entry) => {
        const raw = await readFile(path.join(TRACE_DIR, entry), "utf8");
        return JSON.parse(raw) as PosterProductionTrace;
      })
  );

  return traces.sort((left, right) => right.created_at.localeCompare(left.created_at));
}

export type PosterProductionTrace = {
  run_id: string;
  input_hash: string;
  created_at: string;
  input: PosterProductionInput;
  status: PosterProductionRun["status"];
  module_trace: string[];
  winner_variant_id: string | null;
  qa_result: PosterProductionRun["stages"]["stage_05_quality_gate"];
  render_artifact_id: string | null;
  performance_event_id: string | null;
  render_contract: PosterProductionRun["render_contract"];
};

function createInputHash(input: PosterProductionInput) {
  return createHash("sha256").update(JSON.stringify(input)).digest("hex").slice(0, 16);
}

export async function createPosterProductionTrace(
  input: PosterProductionInput,
  run: Omit<PosterProductionRun, "trace">
): Promise<PosterProductionTrace> {
  const backend = resolveTraceBackend();
  const trace: PosterProductionTrace = {
    run_id: randomUUID(),
    input_hash: createInputHash(input),
    created_at: new Date().toISOString(),
    input,
    status: run.status,
    module_trace: [
      "code-intelligence.graph",
      "scale-intelligence.detect-industry",
      "v6-pro.runtime",
      "v4-poster.engine",
      "poster-intelligence.qa",
      ...(run.status === "render_ready" ? [] : ["poster-intelligence.autofix"]),
    ],
    winner_variant_id: (run.winner as { variant?: string } | null)?.variant || null,
    qa_result: run.stages.stage_05_quality_gate,
    render_artifact_id: null,
    performance_event_id: null,
    render_contract: run.render_contract,
  };

  if (backend === "disabled") {
    return trace;
  }

  if (backend === "supabase") {
    await writeSupabaseTrace(trace);
    return trace;
  }

  await writeFilesystemTrace(trace);

  return trace;
}

export async function listPosterProductionTraces(limit = 20): Promise<PosterProductionTrace[]> {
  const backend = resolveTraceBackend();
  if (backend === "disabled") return [];
  if (backend === "supabase") return listSupabaseTraces(limit);
  return listFilesystemTraces(limit);
}
