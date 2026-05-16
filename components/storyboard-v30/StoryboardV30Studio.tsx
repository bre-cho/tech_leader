"use client";

import { useState } from "react";
import SalesEngineV3Panel from "@/components/storyboard-v30/SalesEngineV3Panel";
import { persistDomainHandoff } from "@/lib/workflow/handoff-client";

export default function StoryboardV30Studio() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch("/api/storyboard/v30/sales-run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        title: "London Fashion Week — 160 Shot Fashion Film",
        format: "fashion_runway",
        mainCharacter: "1 cô gái / female model",
        location: "London Fashion Week",
        aspectRatio: "1:1",
        totalShots: 160,
        targetDurationSec: 240,
        requestedPhases: ["setup", "backstage", "runway", "after_party"],
        identityDna: {
          faceLock: true,
          wardrobeContinuity: true,
          hairMakeupContinuity: true,
          characterNotes: "same female fashion model, cinematic editorial beauty identity, confident runway persona"
        },
        providers: {
          still: "hidream",
          video: "veo",
          motionAlt: "runway"
        },
        outputDir: "storage/v30-storyboard-agent/demo",
        salesEngine: {
          enabled: true,
          productName: "son môi đỏ luxury Dior/YSL",
          category: "lipstick",
          brief: "Micro contrast on lips + lipstick only, eye highlight boost nhẹ, skin matte, lipstick touching lips",
          duration: 15,
          platform: "shorts",
          aspectRatio: "9:16",
          language: "vi",
          preserveIdentity: true,
          preserveProductShape: true,
          goal: "sale"
        }
      })
    });
    const data = await res.json();
    setResult(data);

    const shots = data?.phases?.flatMap((phase: any) => phase?.shots || []) ?? [];
    const storyboard = shots.slice(0, 60).map((shot: any, index: number) => ({
      title: shot?.title || `Storyboard shot ${index + 1}`,
      description: `${shot?.phase || "runtime"} - ${shot?.camera || "cam"} - ${shot?.movement || "motion"}`,
    }));

    persistDomainHandoff("storyboard-v30", {
      workflowId: data?.workflow_id || data?.timeline?.id || undefined,
      request: { storyboard },
      providerPayloadResult: data?.providerPayloads || {},
      videoFlowCompile: data?.videoFlowCompile || { status: data?.status || "ready", timeline: data?.timeline || null },
    });

    setLoading(false);
  }

  const shots = result?.phases?.flatMap((p: any) => p.shots) ?? [];

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-7xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">V30 — Storyboard Agent: London Fashion Week Runtime</h1>
          <p className="mt-2 text-neutral-300">Phase-aware 160-shot fashion event storyboard: Setup → Backstage → Runway → After Party.</p>
          <button onClick={run} disabled={loading} className="primary-button mt-5">
            {loading ? "Đang dựng storyboard..." : "Run Storyboard Agent V30"}
          </button>
        </div>

        {result && (
          <>
            <Panel title="Analysis + Verification" data={{ analysis: result.analysis, verification: result.verification }} />
            <Panel title="Timeline" data={result.timeline} />
            <Panel title="Provider Batches" data={{
              stillItems: result.providerPayloads?.stillKeyframes?.items?.length,
              videoItems: result.providerPayloads?.videoShots?.items?.length,
              altMotionItems: result.providerPayloads?.altMotion?.items?.length,
              salesVideoItems: result.providerPayloads?.salesVideoShots?.items?.length,
              salesKeyframeItems: result.providerPayloads?.salesKeyframes?.items?.length
            }} />
            <SalesEngineV3Panel
              salesEngine={result.salesEngineV3}
              verification={result.verification}
              providerPayloads={result.providerPayloads}
            />
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-xl font-semibold">Shot List</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {shots.slice(0, 36).map((s: any) => (
                  <div key={s.id} className="rounded-2xl border border-neutral-800 bg-neutral-950 p-4">
                    <div className="text-sm text-neutral-400">#{s.id} · {s.phase}</div>
                    <div className="font-semibold">{s.title}</div>
                    <div className="mt-2 text-sm text-neutral-300">{s.camera} · {s.movement}</div>
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
