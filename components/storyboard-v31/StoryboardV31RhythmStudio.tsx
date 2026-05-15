"use client";

import { useState } from "react";

export default function StoryboardV31RhythmStudio() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch("/api/storyboard/v31/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        title: "Fashion Shorts Rhythm Engine",
        concept: "London Fashion Week cinematic runway short",
        platform: "youtube_shorts",
        aspectRatio: "9:16",
        musicBpm: 118,
        targetDurationSec: 35,
        mainCharacter: "same female fashion model",
        location: "London Fashion Week",
        fashionDna: "luxury editorial runway, cinematic spotlight, confident model identity",
        provider: { image: "hidream", video: "veo", motionFallback: "runway" },
        outputDir: "storage/v31-storyboard-rhythm/demo"
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main className="brain-route-main">
      <section className="brain-route-wrap">
        <div className="brain-route-head">
          <p className="brain-route-kicker">V31 Runtime</p>
          <h1 className="brain-route-title">Storyboard Retention and Rhythm Engine</h1>
          <p className="brain-route-desc">
            Rhythm graph, micro hooks, camera language, runway escalation, social proof, retention validation, and render queue.
          </p>
          <button onClick={run} disabled={loading} className="mt-5 brain-primary-btn">
            {loading ? "Đang tối ưu storyboard..." : "Run V31 Runtime"}
          </button>
        </div>

        {result && (
          <>
            <Panel title="Verification" data={result.verification} />
            <Panel title="Energy + Retention" data={{ energy: result.energyValidation, retention: result.retentionValidation, shortsTimeline: result.shortsTimeline }} />
            <Panel title="Optimization Engines" data={{ microHooks: result.microHooks, cameraLanguage: result.cameraLanguage, runwayEscalation: result.runwayEscalation, socialProof: result.socialProof }} />
            <Panel title="Provider Payload Summary" data={{ imageItems: result.providerPayloads?.imageKeyframes?.items?.length, videoItems: result.providerPayloads?.videoShots?.items?.length, renderQueue: result.providerPayloads?.renderQueue?.length }} />
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-xl font-semibold">Rhythm Graph</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {result.rhythmGraph?.map((r: any) => (
                  <div key={r.shotId} className="rounded-2xl border border-neutral-800 bg-neutral-950 p-4">
                    <div className="text-sm text-neutral-400">Shot #{r.shotId} · {r.hookType}</div>
                    <div className="mt-2 text-sm">Energy {r.energy} · Motion {r.motion} · Face {r.facePriority} · Social {r.socialProof}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </section>
    </main>
  );
}

function Panel({ title, data }: { title: string; data: any }) {
  return (
    <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
      <h2 className="text-xl font-semibold">{title}</h2>
      <pre className="mt-3 max-h-[460px] overflow-auto whitespace-pre-wrap text-sm text-neutral-300">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
