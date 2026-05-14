export default function LuxuryFaceScoringPanel({result}: {result: any}) {
  return (
    <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
      <h2 className="text-xl font-semibold">Luxury Face Scoring</h2>
      <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">
        {result ? JSON.stringify({
          scoring: result.luxury_face_scoring,
          verification: result.verification,
          winner_dna: result.winner_dna
        }, null, 2) : "Beauty scoring sẽ hiển thị tại đây."}
      </pre>
    </div>
  );
}
