"use client";

import { useState } from "react";
import FaceBalancePanel from "./FaceBalancePanel";
import NoseContourEngine from "./NoseContourEngine";
import BeautyDepthPreview from "./BeautyDepthPreview";
import LuxuryFaceScoringPanel from "./LuxuryFaceScoringPanel";

export default function FacialAestheticStudio() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const res = await fetch("/api/facial-aesthetic/v28-1/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        brandName: "Demo Beauty",
        industry: "cosmetic_brand",
        targetAudience: "Vietnamese women 22-35",
        faceDescription: "soft oval balanced face, high elegant nose bridge, large bright almond eyes, soft natural full lips, soft feminine jawline",
        makeupDirection: "clean semi-matte K-beauty makeup, soft luxury contour, premium glow highlight, natural slim nose definition, soft pink feminine warmth",
        commercialGoal: "conversion",
        saveWinnerDna: true
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-white p-8">
      <section className="max-w-6xl mx-auto grid gap-6">
        <div className="rounded-3xl border border-neutral-800 p-6 bg-neutral-900">
          <h1 className="text-3xl font-bold">V28.1 — Facial Aesthetic Perception Engine</h1>
          <p className="text-neutral-300 mt-2">AI Beauty Commerce Intelligence + AI Facial Aesthetic Reasoning.</p>
          <button onClick={run} disabled={loading} className="mt-5 rounded-2xl bg-white text-black px-5 py-3 font-semibold">
            {loading ? "Đang phân tích..." : "Run Facial Aesthetic Engine"}
          </button>
        </div>

        <FaceBalancePanel result={result} />
        <NoseContourEngine result={result} />
        <BeautyDepthPreview result={result} />
        <LuxuryFaceScoringPanel result={result} />

        {result && (
          <div className="rounded-3xl border border-neutral-800 p-5 bg-neutral-900">
            <h2 className="text-xl font-semibold">Prompt Enhancer</h2>
            <pre className="mt-3 text-sm whitespace-pre-wrap text-neutral-300">{result.prompt_enhancer}</pre>
          </div>
        )}
      </section>
    </main>
  );
}
