import type { FacialAestheticResult } from "@/lib/facial-aesthetic";

export function CommercialFaceScoreCard({ result }: { result: FacialAestheticResult }) {
  return (
    <section className="rounded-2xl border p-4 shadow-sm">
      <h3 className="text-lg font-semibold">Commercial Face Score</h3>
      <div className="mt-2 text-4xl font-bold">{result.winnerDNA.finalScore}</div>
      <p className="mt-2 text-sm text-neutral-600">{result.winnerDNA.reason}</p>
      {result.issues.length > 0 && (
        <div className="mt-4 rounded-xl bg-amber-50 p-3">
          {result.issues.map((issue) => (
            <p key={issue.code} className="text-sm">
              <b>{issue.severity.toUpperCase()}:</b> {issue.message} — {issue.fix}
            </p>
          ))}
        </div>
      )}
    </section>
  );
}
