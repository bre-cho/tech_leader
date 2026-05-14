"use client";

import { useState } from "react";

export default function BeautyPerceptionStudio() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch("/api/beauty-perception/v29/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        brandName: "Demo Beauty KOL",
        campaignName: "soft_korean_beauty_v29",
        productName: "Glow Serum",
        platform: "tiktok",
        lightingStyle: "KOREAN_SOFT",
        identityDna: {
          faceGeometry: "soft oval balanced face",
          eyeRatio: "large bright almond eyes with soft aegyo-sal",
          lipRatio: "natural lips, slightly fuller lower lip",
          noseSoftness: "soft refined high nose bridge",
          eyebrowCurvature: "natural thin straight eyebrows",
          skinTone: "light neutral-warm Asian skin with pink undertone",
          moleMap: "tiny mole near cheek/nose wing if identity reference requires it",
          aegyoSal: "soft natural aegyo-sal",
          jawSoftness: "soft feminine jawline",
          hairTexture: "long dark hair with natural shine and soft face framing",
          smileSignature: "micro warm smile"
        },
        desiredSignals: [
          "direct eye contact",
          "slight smile",
          "head tilt",
          "collarbone elegance",
          "soft hair framing",
          "warm backlight",
          "shallow DOF",
          "finger near lips"
        ],
        references: [
          { kind: "identity_ref", label: "face reference", uri: "/refs/identity.png", lockStrength: 0.95 },
          { kind: "makeup_ref", label: "K-beauty makeup", uri: "/refs/makeup.png", lockStrength: 0.85 },
          { kind: "pose_ref", label: "finger near lips pose", uri: "/refs/pose.png", lockStrength: 0.8 }
        ],
        sceneCount: 5,
        saveMemory: true
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-7xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">V29 — Beauty Perception Graph Engine</h1>
          <p className="mt-2 text-neutral-300">
            Beauty DNA Graph → Femininity Signal Graph → Attention Routing → CTR Prediction → Provider Handoff → Winner DNA.
          </p>
          <button onClick={run} disabled={loading} className="mt-5 rounded-2xl bg-white px-5 py-3 font-semibold text-black">
            {loading ? "Đang chạy V29..." : "Run V29 Engine"}
          </button>
        </div>

        {result && (
          <>
            <Panel title="Status + Score" data={{ status: result.status, commercialBeautyScore: result.commercialBeautyScore, socialCtrPrediction: result.socialCtrPrediction }} />
            <Panel title="Beauty Graph" data={{ graph_id: result.graph.graph_id, nodes: result.graph.nodes.length, edges: result.graph.edges.length }} />
            <Panel title="Scene Spec" data={result.sceneSpec} />
            <Panel title="Provider Route" data={result.providerRoute} />
            <Panel title="Memory DNA" data={result.memoryDna ?? "Not saved"} />
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-xl font-semibold">Prompt Pack</h2>
              <pre className="mt-3 whitespace-pre-wrap text-sm text-neutral-300">{JSON.stringify(result.promptPack, null, 2)}</pre>
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
      <pre className="mt-3 whitespace-pre-wrap text-sm text-neutral-300">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
