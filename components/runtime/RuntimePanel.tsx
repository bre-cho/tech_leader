import type { DesignStudioResponse } from "@/lib/design/pipeline-api";

type RuntimePanelProps = {
  error: string | null;
  isRunning: boolean;
  result: DesignStudioResponse | null;
};

function formatGateStatus(promotionGate: Record<string, unknown> | null | undefined): string {
  if (!promotionGate) {
    return "Promotion gate waiting for verification.";
  }

  const passed = promotionGate.passed;
  const status = typeof passed === "boolean" ? (passed ? "GO" : "HOLD") : "UNKNOWN";
  return `Promotion gate status: ${status}`;
}

export function RuntimePanel({ error, isRunning, result }: RuntimePanelProps) {
  const phase1 = isRunning
    ? "Research Agent scanning winner DNA..."
    : "Research Agent idle.";
  const phase2 = result?.storyboard?.length
    ? `Storyboard Agent produced ${result.storyboard.length} scenes.`
    : "Storyboard Agent waiting for run.";
  const phase3 = formatGateStatus(result?.promotion_gate);

  return (
    <aside className="runtime-panel">
      <div className="pipeline-card">
        <div className="section-eyebrow">LIVE RUNTIME</div>

        <h2>Agent Runtime</h2>

        <div className="runtime-log">{phase1}</div>

        <div className="runtime-log">{phase2}</div>

        <div className="runtime-log">{phase3}</div>

        {error ? <div className="runtime-log">API error: {error}</div> : null}
      </div>
    </aside>
  );
}
