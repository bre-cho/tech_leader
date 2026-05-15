import type { ImageConcept } from "@/lib/design/pipeline-api";

type ImageBattleBoardProps = {
  bestConcept: ImageConcept | null;
  concepts: ImageConcept[];
};

function score(value: number | undefined): string {
  return typeof value === "number" ? String(value) : "--";
}

export function ImageBattleBoard({ bestConcept, concepts }: ImageBattleBoardProps) {
  const source = concepts.length ? concepts : bestConcept ? [bestConcept] : [];

  return (
    <div className="pipeline-card">
      <div className="section-eyebrow">IMAGE BATTLE VIEW</div>

      <h2>So sanh concept chien thang</h2>

      <div className="battle-grid">
        {source.map((image) => (
          <div className="battle-card" key={image.concept_id}>
            <div className="battle-preview">{image.headline || image.concept_id}</div>

            <div className="score-list">
              <div className="score-row">
                <span>Attention</span>
                <strong>{score(image.score?.attention_score)}</strong>
              </div>
              <div className="score-row">
                <span>Trust</span>
                <strong>{score(image.score?.trust_score)}</strong>
              </div>
              <div className="score-row">
                <span>Conversion</span>
                <strong>{score(image.score?.conversion_score)}</strong>
              </div>
              <div className="score-row">
                <span>Brand Recall</span>
                <strong>{score(image.score?.brand_fit_score)}</strong>
              </div>
            </div>

            <button className="secondary-button" type="button">
              {bestConcept?.concept_id === image.concept_id ? "Winner" : image.cta || "Candidate"}
            </button>
          </div>
        ))}

        {!source.length ? <div className="battle-card">Run pipeline to get concept battle data.</div> : null}
      </div>
    </div>
  );
}
