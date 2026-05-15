import { VideoHandoffPanel } from "@/components/handoff/VideoHandoffPanel";
import { ImageBattleBoard } from "@/components/image-battle/ImageBattleBoard";
import { WinnerSelectionPanel } from "@/components/image-battle/WinnerSelectionPanel";
import { MemoryGraphPanel } from "@/components/memory/MemoryGraphPanel";
import { ReleaseGatePanel } from "@/components/release-gate/ReleaseGatePanel";
import { StoryboardWorkspace } from "@/components/storyboard/StoryboardWorkspace";
import type { DesignStudioRequest, DesignStudioResponse } from "@/lib/design/pipeline-api";

type ProjectWorkspaceProps = {
  brief: DesignStudioRequest;
  error: string | null;
  handoffError: string | null;
  handoffLoading: boolean;
  handoffStatus: string | null;
  isRunning: boolean;
  onOpenVideoStudio: () => void;
  onRun: () => void;
  onUpdateBrief: <K extends keyof DesignStudioRequest>(
    field: K,
    value: DesignStudioRequest[K],
  ) => void;
  result: DesignStudioResponse | null;
};

export function ProjectWorkspace({
  brief,
  error,
  handoffError,
  handoffLoading,
  handoffStatus,
  isRunning,
  onOpenVideoStudio,
  onRun,
  onUpdateBrief,
  result,
}: ProjectWorkspaceProps) {
  return (
    <section className="project-workspace">
      <div className="workspace-header">
        <div>
          <div className="eyebrow">PROJECT PIPELINE OS</div>
          <h1>IMAGE - STORYBOARD - VIDEO</h1>
        </div>

        <button className="primary-button" type="button" onClick={onRun} disabled={isRunning}>
          {isRunning ? "Running..." : "Start Pipeline"}
        </button>
      </div>

      <div className="pipeline-card">
        <div className="section-eyebrow">CREATIVE BRIEF</div>
        <div className="brief-grid">
          <label className="brief-field">
            Industry
            <input value={brief.industry} onChange={(event) => onUpdateBrief("industry", event.target.value)} />
          </label>
          <label className="brief-field">
            Product
            <input value={brief.product} onChange={(event) => onUpdateBrief("product", event.target.value)} />
          </label>
          <label className="brief-field">
            Audience
            <input value={brief.audience} onChange={(event) => onUpdateBrief("audience", event.target.value)} />
          </label>
          <label className="brief-field">
            Channel
            <input value={brief.channel} onChange={(event) => onUpdateBrief("channel", event.target.value)} />
          </label>
          <label className="brief-field">
            Goal
            <input value={brief.goal} onChange={(event) => onUpdateBrief("goal", event.target.value)} />
          </label>
          <label className="brief-field">
            Brand
            <input value={brief.brand_name} onChange={(event) => onUpdateBrief("brand_name", event.target.value)} />
          </label>
          <label className="brief-field">
            Budget
            <select
              value={brief.budget_tier}
              onChange={(event) =>
                onUpdateBrief(
                  "budget_tier",
                  event.target.value as DesignStudioRequest["budget_tier"],
                )
              }
            >
              <option value="low">low</option>
              <option value="mid">mid</option>
              <option value="premium">premium</option>
            </select>
          </label>
          <label className="brief-field">
            Dry run
            <select
              value={brief.dry_run ? "true" : "false"}
              onChange={(event) => onUpdateBrief("dry_run", event.target.value === "true")}
            >
              <option value="false">false</option>
              <option value="true">true</option>
            </select>
          </label>
        </div>
        {error ? <div className="brief-error">{error}</div> : null}
      </div>

      <ImageBattleBoard bestConcept={result?.best_concept ?? null} concepts={result?.image_concepts ?? []} />
      <WinnerSelectionPanel bestConcept={result?.best_concept ?? null} />
      <StoryboardWorkspace scenes={result?.storyboard ?? []} />
      <VideoHandoffPanel
        handoffError={handoffError}
        handoffLoading={handoffLoading}
        handoffStatus={handoffStatus}
        onOpenVideoStudio={onOpenVideoStudio}
        promotionGate={result?.promotion_gate ?? null}
        providerPreview={result?.video_concept_preview ?? null}
      />

      <div className="workspace-grid">
        <ReleaseGatePanel
          promotionGate={result?.promotion_gate ?? null}
          verification={result?.verification ?? null}
        />
        <MemoryGraphPanel
          memoryUpdate={result?.memory_update ?? null}
          recalledWinnerDna={result?.recalled_winner_dna ?? []}
        />
      </div>
    </section>
  );
}
