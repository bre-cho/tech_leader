"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

const defaultPayload = {
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
  outputDir: "storage/v31-storyboard-rhythm/demo",
};

export default function StoryboardV31RhythmStudio() {
  const searchParams = useSearchParams();
  const source = searchParams.get("source");
  const autoRun = searchParams.get("autorun") === "1";

  const [payload, setPayload] = useState<any>(defaultPayload);
  const [handoffMeta, setHandoffMeta] = useState<any>(null);
  const [videoFlowMeta, setVideoFlowMeta] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(overridePayload?: any) {
    setLoading(true);
    setError(null);
    const isDomEventLike =
      overridePayload &&
      typeof overridePayload === "object" &&
      ("nativeEvent" in overridePayload || "currentTarget" in overridePayload);
    const body = isDomEventLike ? payload : (overridePayload ?? payload);
    const res = await fetch("/api/storyboard/v31/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data?.error || "V31 runtime failed");
      setLoading(false);
      return;
    }
    setResult(data);
    setLoading(false);
  }

  useEffect(() => {
    if (source !== "pipeline-os") {
      return;
    }

    const raw = sessionStorage.getItem("pipeline-os:v31-handoff");
    if (!raw) {
      return;
    }

    try {
      const parsed = JSON.parse(raw);
      if (parsed?.request) {
        setPayload(parsed.request);
      }
      if (parsed?.providerPayloadResult) {
        setHandoffMeta(parsed.providerPayloadResult);
      }
      if (parsed?.videoFlowCompile) {
        setVideoFlowMeta(parsed.videoFlowCompile);
      }
      if (autoRun && parsed?.request) {
        void run(parsed.request);
      }
    } catch {
      setError("Cannot parse pipeline handoff payload.");
    }
  }, [autoRun, source]);

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-7xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">V31 — Storyboard Retention + Rhythm Engine</h1>
          <p className="mt-2 text-neutral-300">
            Rhythm Graph → Micro Hooks → Camera Language → Runway Escalation → Social Proof → Retention Validator → Render Queue.
          </p>
          <button onClick={() => { void run(); }} disabled={loading} className="mt-5 rounded-2xl bg-white px-5 py-3 font-semibold text-black">
            {loading ? "Đang tối ưu storyboard..." : "Run V31 Runtime"}
          </button>
          {source === "pipeline-os" ? (
            <p className="mt-3 text-sm text-neutral-400">Payload sourced from Pipeline OS handoff.</p>
          ) : null}
          {error ? <p className="mt-3 text-sm text-red-300">{error}</p> : null}
        </div>

        {handoffMeta ? <Panel title="Pipeline Handoff" data={handoffMeta} /> : null}
        {videoFlowMeta ? <Panel title="VideoFlow Compile (Ready To Render)" data={videoFlowMeta} /> : null}

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
