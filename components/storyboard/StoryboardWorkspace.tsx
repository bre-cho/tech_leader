type StoryboardWorkspaceProps = {
  scenes: Array<Record<string, unknown>>;
};

function readString(scene: Record<string, unknown>, keys: string[], fallback: string): string {
  for (const key of keys) {
    const value = scene[key];
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }
  return fallback;
}

export function StoryboardWorkspace({ scenes }: StoryboardWorkspaceProps) {
  return (
    <div className="pipeline-card">
      <div className="section-eyebrow">STORYBOARD EXTRACTION</div>

      <h2>Scene Dependency Graph</h2>

      <div className="storyboard-grid">
        {scenes.map((scene, index) => (
          <div className="scene-card" key={`${readString(scene, ["scene_id", "title"], "scene")}-${index}`}>
            <div className="scene-index">Scene {String(index + 1).padStart(2, "0")}</div>

            <h3>{readString(scene, ["title", "shot", "scene"], "Untitled scene")}</h3>

            <div className="scene-meta">
              <div>Camera: {readString(scene, ["camera", "camera_move"], "n/a")}</div>
              <div>Motion: {readString(scene, ["motion", "action"], "n/a")}</div>
              <div>Subtitle: {readString(scene, ["subtitle", "copy"], "n/a")}</div>
              <div>Provider: {readString(scene, ["provider", "engine"], "n/a")}</div>
              <div>Duration: {readString(scene, ["duration", "length"], "n/a")}</div>
            </div>
          </div>
        ))}

        {!scenes.length ? <div className="scene-card">No storyboard yet. Run pipeline first.</div> : null}
      </div>
    </div>
  );
}
