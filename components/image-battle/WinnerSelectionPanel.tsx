import type { ImageConcept } from "@/lib/design/pipeline-api";

type WinnerSelectionPanelProps = {
  bestConcept: ImageConcept | null;
};

export function WinnerSelectionPanel({ bestConcept }: WinnerSelectionPanelProps) {
  const title = bestConcept?.headline || "No winner yet";
  const description = bestConcept?.prompt || "Run pipeline to generate winner concept.";

  return (
    <div className="pipeline-card winner-panel">
      <div className="winner-preview">{bestConcept?.concept_id || "WINNER"}</div>

      <div className="winner-content">
        <div className="section-eyebrow">WINNER DNA</div>

        <h2>{title}</h2>

        <p>{description}</p>

        <div className="winner-actions">
          <button className="btn-primary" type="button">
            Generate Storyboard
          </button>

          <button className="btn-secondary" type="button">
            Save To Memory
          </button>
        </div>
      </div>
    </div>
  );
}
