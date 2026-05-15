import type { EngineSignal } from "@/lib/facial-aesthetic";

export function FaceBalancePanel({ signal }: { signal: EngineSignal }) {
  return (
    <section className="rounded-2xl border p-4 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">Cân bằng gương mặt</h3>
        <strong className="text-2xl">{signal.score}</strong>
      </div>
      <p className="mt-2 text-sm text-neutral-600">{signal.recommendation}</p>
      <ul className="mt-3 list-disc pl-5 text-sm text-neutral-700">
        {signal.evidence.map((e) => (
          <li key={e}>{e}</li>
        ))}
      </ul>
    </section>
  );
}
