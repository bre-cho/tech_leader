"use client";

import { useState } from "react";
import AvatarIdentityBuilder from "./AvatarIdentityBuilder";
import BeautyKOLPersonaPanel from "./BeautyKOLPersonaPanel";
import MakeupAvatarPreview from "./MakeupAvatarPreview";
import IndustryAvatarPresetGrid from "./IndustryAvatarPresetGrid";
import AvatarConsistencyPanel from "./AvatarConsistencyPanel";
import AvatarRender8KPanel from "./AvatarRender8KPanel";

export default function VirtualAvatarStudio() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function createAvatar() {
    setLoading(true);
    const payload = {
      brandName: "Demo Beauty",
      personaType: "kol_beauty",
      industry: "cosmetic_brand",
      faceDescription: "oval face, warm light Asian skin tone, almond eyes, soft full lips, natural soft bridge",
      productContext: "premium serum campaign",
      targetAudience: "Vietnamese women 22-35",
      renderUsage: ["poster", "thumbnail", "ads", "lookbook", "short video"],
      quality: "8K",
      saveMemory: true
    };

    const res = await fetch("/api/beauty-avatar/create", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-white p-8">
      <section className="max-w-6xl mx-auto grid gap-6">
        <div className="rounded-3xl border border-neutral-800 p-6 bg-neutral-900">
          <h1 className="text-3xl font-bold">V26.1 — AI Virtual Beauty Avatar Engine</h1>
          <p className="text-neutral-300 mt-2">Personal Beauty AI → KOL Beauty → Studio Makeup → Wedding Studio → Spa → Fashion / Cosmetic / Clinic / TikTok Creator.</p>
          <button onClick={createAvatar} disabled={loading} className="mt-5 rounded-2xl bg-white text-black px-5 py-3 font-semibold">
            {loading ? "Đang tạo avatar..." : "Create Beauty Avatar"}
          </button>
          {result && (
            <button
              onClick={() => {
                const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = "beauty-avatar-result.json";
                a.click();
                URL.revokeObjectURL(a.href);
              }}
              className="mt-3 rounded-2xl border border-neutral-600 px-5 py-3 font-semibold hover:border-white"
            >
              ⬇ Tải xuống kết quả
            </button>
          )}
        </div>

        <IndustryAvatarPresetGrid />
        <AvatarIdentityBuilder result={result} />
        <BeautyKOLPersonaPanel result={result} />
        <MakeupAvatarPreview result={result} />
        <AvatarConsistencyPanel result={result} />
        <AvatarRender8KPanel result={result} />
      </section>
    </main>
  );
}
