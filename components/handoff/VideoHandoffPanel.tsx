"use client";

type VideoHandoffPanelProps = {
  handoffError: string | null;
  handoffLoading: boolean;
  handoffStatus: string | null;
  onOpenVideoStudio: () => void;
  promotionGate: Record<string, unknown> | null;
  providerPreview: Record<string, unknown> | null;
};

function handoffLabel(promotionGate: Record<string, unknown> | null): string {
  if (!promotionGate) {
    return "Waiting for validation";
  }
  return promotionGate.passed === true ? "Ready for handoff" : "Gate hold";
}

export function VideoHandoffPanel({
  handoffError,
  handoffLoading,
  handoffStatus,
  onOpenVideoStudio,
  promotionGate,
  providerPreview,
}: VideoHandoffPanelProps) {
  const previewText = providerPreview
    ? JSON.stringify(providerPreview).slice(0, 180)
    : "No provider payload yet.";

  return (
    <div className="pipeline-card handoff-panel">
      <div>
        <div className="section-eyebrow">VIDEO HANDOFF</div>

        <h2>Send To Realtime Video Studio</h2>

        <p>{handoffLabel(promotionGate)}. {previewText}</p>
      </div>

      <button className="primary-button" type="button" onClick={onOpenVideoStudio} disabled={handoffLoading}>
        {handoffLoading ? "Handoff running..." : "Open Video Studio"}
      </button>

      <div className="scene-meta">
        <div>Handoff + compile status: {handoffStatus || "not started"}</div>
        {handoffError ? <div>{handoffError}</div> : null}
      </div>
    </div>
  );
}
