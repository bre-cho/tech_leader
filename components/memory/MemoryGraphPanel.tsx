type MemoryGraphPanelProps = {
  memoryUpdate: Record<string, unknown> | null;
  recalledWinnerDna: Array<Record<string, unknown>>;
};

function dnaLabels(nodes: Array<Record<string, unknown>>): string[] {
  return nodes
    .map((node) => {
      const name = node.name;
      if (typeof name === "string" && name.trim()) {
        return name;
      }
      const title = node.title;
      if (typeof title === "string" && title.trim()) {
        return title;
      }
      return null;
    })
    .filter((value): value is string => Boolean(value));
}

export function MemoryGraphPanel({ memoryUpdate, recalledWinnerDna }: MemoryGraphPanelProps) {
  const labels = dnaLabels(recalledWinnerDna);

  return (
    <div className="pipeline-card">
      <div className="section-eyebrow">VISUAL DNA GRAPH</div>

      <h2>Luxury Beauty Memory</h2>

      <div className="memory-node-list">
        {labels.map((label) => (
          <div className="memory-node" key={label}>
            {label}
          </div>
        ))}
        {!labels.length ? <div className="memory-node">No recalled winner DNA</div> : null}
      </div>

      <div className="scene-meta">
        <div>Memory update: {memoryUpdate ? "available" : "pending"}</div>
      </div>
    </div>
  );
}
