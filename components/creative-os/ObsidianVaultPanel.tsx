export function ObsidianVaultPanel() {
  const folders = [
    'projects',
    'storyboards',
    'visual_dna',
    'runtime_logs',
    'winner_patterns',
    'provider_runtime',
    'memory_graph',
  ];

  return (
    <section className="os-card">
      <div className="os-eyebrow">OBSIDIAN VAULT</div>
      <h2>Persistent Creative Memory</h2>

      {folders.map((folder) => (
        <div className="os-status" key={folder}>
          <span>{folder}</span>
          <strong>ACTIVE</strong>
        </div>
      ))}
    </section>
  );
}
