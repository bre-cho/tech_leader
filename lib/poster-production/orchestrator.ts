export * from "../../backend/app/vendor/veo_poster_intelligence/poster-production/orchestrator";
export type PosterProductionTrace = {
  trace_id: string;
  events: string[];
};

export async function createPosterProductionTrace(_input: unknown, _run: unknown): Promise<PosterProductionTrace> {
  return { trace_id: "trace_mock", events: ["mock_trace"] };
}
