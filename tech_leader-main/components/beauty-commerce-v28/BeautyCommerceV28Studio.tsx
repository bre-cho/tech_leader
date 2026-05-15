"use client";

import { useState, useRef } from "react";

export default function BeautyCommerceV28Studio() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [avatarImage, setAvatarImage] = useState<string | null>(null);
  const [avatarName, setAvatarName] = useState<string | null>(null);
  const [makeupImage, setMakeupImage] = useState<string | null>(null);
  const [makeupName, setMakeupName] = useState<string | null>(null);
  const [productImage, setProductImage] = useState<string | null>(null);
  const [productName, setProductName] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const avatarRef = useRef<HTMLInputElement>(null);
  const makeupRef = useRef<HTMLInputElement>(null);
  const productRef = useRef<HTMLInputElement>(null);

  function makeUploadHandler(setter: (v: string) => void, nameSetter: (v: string) => void) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
        setUploadError("Chỉ chấp nhận JPEG, PNG hoặc WebP");
        return;
      }
      const reader = new FileReader();
      reader.onload = () => { setter(reader.result as string); nameSetter(file.name); setUploadError(null); };
      reader.onerror = () => setUploadError("Lỗi đọc file ảnh");
      reader.readAsDataURL(file);
    };
  }

  async function run() {
    setLoading(true);
    const references: { kind: string; label: string; uri: string; lockStrength: number }[] = [
      ...(avatarImage ? [{ kind: "identity", label: "Avatar face ref (uploaded)", uri: avatarImage, lockStrength: 0.92 }] : [{ kind: "identity", label: "Avatar face ref", uri: "/refs/avatar.png", lockStrength: 0.92 }]),
      ...(makeupImage ? [{ kind: "makeup", label: "Makeup ref (uploaded)", uri: makeupImage, lockStrength: 0.85 }] : [{ kind: "makeup", label: "K-beauty makeup ref", uri: "/refs/makeup.png", lockStrength: 0.85 }]),
      ...(productImage ? [{ kind: "product", label: "Product ref (uploaded)", uri: productImage, lockStrength: 0.88 }] : []),
      { kind: "lighting", label: "warm lifestyle lighting", uri: "/refs/lighting.png", lockStrength: 0.8 }
    ];
    const res = await fetch("/api/beauty-commerce/v28-2/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        brandName: "Demo Beauty",
        productName: "Glow Serum",
        productType: "serum bottle",
        industry: "tiktok_beauty_ads",
        avatarDna: "realistic Vietnamese/Asian beauty KOL, natural skin texture, soft feminine commercial look, warm smile, premium makeup glow",
        campaignGoal: "conversion",
        channel: "tiktok",
        sceneCount: 5,
        durationSec: 15,
        references,
        outputDir: "storage/beauty-commerce-v28/demo",
        saveWinnerDna: true
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  function UploadZone({ label, image, name, inputRef, onChange, color = "#4ade80" }: {
    label: string; image: string | null; name: string | null;
    inputRef: React.RefObject<HTMLInputElement | null>;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    color?: string;
  }) {
    return (
      <div style={{ display: "grid", gap: "0.4rem" }}>
        <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>{label}</label>
        <div onClick={() => inputRef.current?.click()} style={{ border: "2px dashed #333", borderRadius: "0.75rem", padding: "0.85rem", cursor: "pointer", background: image ? "#0d1a12" : "#0a0a0f", display: "flex", alignItems: "center", gap: "0.6rem", transition: "all .15s" }}>
          <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" onChange={onChange} style={{ display: "none" }} />
          {image ? (
            <><img src={image} alt={label} style={{ width: 40, height: 40, borderRadius: "0.4rem", objectFit: "cover" }} />
            <p style={{ margin: 0, color, fontSize: "0.8rem", fontWeight: 600 }}>✅ {name}</p></>
          ) : (
            <p style={{ margin: 0, color: "#666", fontSize: "0.82rem", lineHeight: 1.4 }}>📸 {label}<br /><span style={{ fontSize: "0.73rem" }}>JPEG, PNG, WebP</span></p>
          )}
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <section className="mx-auto grid max-w-6xl gap-6">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <h1 className="text-3xl font-bold">V28.2 + V28.3 Beauty Commerce Engine</h1>
          <p className="mt-2 text-neutral-300">
            Banana Multi-Reference + Femininity Commerce + Social Beauty Commerce Video runtime.
          </p>

          {/* Upload row */}
          <div style={{ marginTop: "1.25rem", display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(3, 1fr)", maxWidth: "660px" }}>
            <UploadZone label="Ảnh nhân vật" image={avatarImage} name={avatarName} inputRef={avatarRef} onChange={makeUploadHandler(setAvatarImage, setAvatarName)} color="#4ade80" />
            <UploadZone label="Ảnh makeup" image={makeupImage} name={makeupName} inputRef={makeupRef} onChange={makeUploadHandler(setMakeupImage, setMakeupName)} color="#f472b6" />
            <UploadZone label="Ảnh sản phẩm" image={productImage} name={productName} inputRef={productRef} onChange={makeUploadHandler(setProductImage, setProductName)} color="#60a5fa" />
          </div>
          {uploadError && <p style={{ marginTop: "0.4rem", color: "#f87171", fontSize: "0.8rem" }}>⚠ {uploadError}</p>}

          <button onClick={run} disabled={loading} className="mt-5 rounded-2xl bg-white px-5 py-3 font-semibold text-black">
            {loading ? "Đang chạy engine..." : "Run V28.2 / V28.3"}
          </button>
        </div>

        {result && (
          <>
            <div>
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
                  const a = document.createElement("a");
                  a.href = URL.createObjectURL(blob);
                  a.download = "beauty-commerce-v28-result.json";
                  a.click();
                  URL.revokeObjectURL(a.href);
                }}
                className="rounded-xl border border-neutral-600 px-4 py-2 text-sm hover:border-white"
              >
                ⬇ Tải xuống kết quả
              </button>
            </div>
            <Panel title="Commercial Score" data={{ status: result.status, commercialScore: result.commercialScore, verification: result.verification }} />
            <Panel title="Provider Payloads" data={result.providerPayloads} />
            <Panel title="Video Plan" data={result.videoPlan} />
            <Panel title="Winner DNA" data={result.winnerDna ?? "Not promoted yet"} />
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-xl font-semibold">Prompt</h2>
              <pre className="mt-3 whitespace-pre-wrap text-sm text-neutral-300">{result.prompt}</pre>
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
