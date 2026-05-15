"use client";

export default function SalesEngineV3Panel({ salesEngine, verification, providerPayloads }: {
  salesEngine?: any;
  verification?: any;
  providerPayloads?: any;
}) {
  if (!salesEngine) return null;

  const score = salesEngine.score;
  const decision = salesEngine.decision;
  const salesVerification = verification?.salesEngineV3;
  const salesQueueCount = providerPayloads?.renderQueueSales?.length ?? 0;

  return (
    <section className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5 text-white">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">AUTO STORYBOARD ENGINE V3 — Sales Layer</h2>
          <p className="mt-1 text-sm text-neutral-400">
            Cơ chế bán hàng → Hook → Desire → Trust/Proof → CTA → Provider Payload → Render Queue
          </p>
        </div>
        <div className={`rounded-2xl px-4 py-2 text-sm font-semibold ${score?.verdict === "READY" ? "bg-emerald-500 text-black" : "bg-yellow-400 text-black"}`}>
          {score?.verdict} · {score?.finalScore}
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Metric label="Category" value={decision?.category} />
        <Metric label="Mechanism" value={decision?.mechanism} />
        <Metric label="Story Arc" value={decision?.storyArc} />
        <Metric label="Render Queue" value={salesQueueCount} />
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {salesEngine.scenes?.map((scene: any) => (
          <div key={scene.sceneId} className="rounded-2xl border border-neutral-800 bg-neutral-950 p-4">
            <div className="text-sm text-neutral-400">{scene.startSec}s-{scene.endSec}s · {scene.scenePurpose}</div>
            <div className="mt-1 font-semibold">{scene.visual}</div>
            <p className="mt-2 text-sm text-neutral-300">{scene.retentionNote}</p>
          </div>
        ))}
      </div>

      <div className="mt-5 rounded-2xl bg-neutral-950 p-4">
        <div className="text-sm font-semibold text-neutral-300">Verification</div>
        <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap text-xs text-neutral-400">
          {JSON.stringify(salesVerification, null, 2)}
        </pre>
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: any }) {
  return (
    <div className="rounded-2xl border border-neutral-800 bg-neutral-950 p-4">
      <div className="text-xs uppercase tracking-wide text-neutral-500">{label}</div>
      <div className="mt-1 font-semibold">{String(value ?? "-")}</div>
    </div>
  );
}
