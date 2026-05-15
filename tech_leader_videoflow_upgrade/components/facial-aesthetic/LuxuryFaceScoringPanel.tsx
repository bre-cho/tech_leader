import type { FacialAestheticResult } from "@/lib/facial-aesthetic";

export function LuxuryFaceScoringPanel({ result }: { result: FacialAestheticResult }) {
  const rows = Object.entries(result.scores);
  return (
    <section className="rounded-2xl border p-4 shadow-sm">
      <h3 className="text-lg font-semibold">Luxury Beauty Scoring</h3>
      <div className="mt-3 grid gap-2">
        {rows.map(([key, value]) => (
          <div key={key} className="flex items-center justify-between rounded-xl bg-neutral-50 px-3 py-2">
            <span className="text-sm">{key.replaceAll("_", " ")}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
