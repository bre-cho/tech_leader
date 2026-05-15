"use client";

import { useState, useRef } from "react";

export default function BeautyCommercePage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [avatarImage, setAvatarImage] = useState<string | null>(null);
  const [avatarName, setAvatarName] = useState<string | null>(null);
  const [productImage, setProductImage] = useState<string | null>(null);
  const [productName, setProductName] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const avatarRef = useRef<HTMLInputElement>(null);
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
    const references: { kind: string; label: string; uri: string; lockStrength: number }[] = [];
    if (avatarImage) references.push({ kind: "identity", label: "Avatar face ref (uploaded)", uri: avatarImage, lockStrength: 0.92 });
    if (productImage) references.push({ kind: "product", label: "Product ref (uploaded)", uri: productImage, lockStrength: 0.88 });
    const res = await fetch("/api/beauty-commerce/v28/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        brandName: "Demo Beauty",
        productName: "Glow Serum",
        productType: "serum bottle",
        industry: "cosmetic_brand",
        targetAudience: "Vietnamese women 22-35",
        campaignGoal: "conversion",
        channel: "tiktok",
        avatarDescription: "realistic virtual Asian beauty KOL, natural skin texture, premium makeup glow",
        outfitStyle: "elegant luxury fashion styling, tasteful soft feminine commercial look",
        poseGoal: "product_demo",
        sensualityLevel: "soft",
        references,
        saveWinnerDna: true
      })
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main className="brain-route-main">
      <section className="brain-route-wrap">
        <div className="brain-route-head">
          <p className="brain-route-kicker">V28 Runtime</p>
          <h1 className="brain-route-title">Beauty Commerce Engine</h1>
          <p className="brain-route-desc">
            Beauty Persona to Facial Consistency to Fashion Perception to Provider Router,
            verification, and Winner DNA update in one execution flow.
          </p>
        </div>

        {/* Image upload row */}
        <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "1fr 1fr", maxWidth: "580px", marginBottom: "0.5rem" }}>
          {/* Avatar */}
          <div style={{ display: "grid", gap: "0.4rem" }}>
            <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>Ảnh avatar / nhân vật</label>
            <div onClick={() => avatarRef.current?.click()} style={{ border: "2px dashed #333", borderRadius: "0.75rem", padding: "0.85rem", cursor: "pointer", background: avatarImage ? "#0d2018" : "#0a0a0f", display: "flex", alignItems: "center", gap: "0.6rem", transition: "all .15s" }}>
              <input ref={avatarRef} type="file" accept="image/jpeg,image/png,image/webp" onChange={makeUploadHandler(setAvatarImage, setAvatarName)} style={{ display: "none" }} />
              {avatarImage ? (
                <><img src={avatarImage} alt="avatar" style={{ width: 40, height: 40, borderRadius: "0.4rem", objectFit: "cover" }} />
                <p style={{ margin: 0, color: "#4ade80", fontSize: "0.8rem", fontWeight: 600 }}>✅ {avatarName}</p></>
              ) : (
                <p style={{ margin: 0, color: "#666", fontSize: "0.82rem", lineHeight: 1.4 }}>📸 Tải ảnh nhân vật<br /><span style={{ fontSize: "0.73rem" }}>JPEG, PNG, WebP</span></p>
              )}
            </div>
          </div>
          {/* Product */}
          <div style={{ display: "grid", gap: "0.4rem" }}>
            <label style={{ fontSize: "0.82rem", color: "#aaa", fontWeight: 600 }}>Ảnh sản phẩm</label>
            <div onClick={() => productRef.current?.click()} style={{ border: "2px dashed #333", borderRadius: "0.75rem", padding: "0.85rem", cursor: "pointer", background: productImage ? "#0d1820" : "#0a0a0f", display: "flex", alignItems: "center", gap: "0.6rem", transition: "all .15s" }}>
              <input ref={productRef} type="file" accept="image/jpeg,image/png,image/webp" onChange={makeUploadHandler(setProductImage, setProductName)} style={{ display: "none" }} />
              {productImage ? (
                <><img src={productImage} alt="product" style={{ width: 40, height: 40, borderRadius: "0.4rem", objectFit: "cover" }} />
                <p style={{ margin: 0, color: "#60a5fa", fontSize: "0.8rem", fontWeight: 600 }}>✅ {productName}</p></>
              ) : (
                <p style={{ margin: 0, color: "#666", fontSize: "0.82rem", lineHeight: 1.4 }}>🛍 Tải ảnh sản phẩm<br /><span style={{ fontSize: "0.73rem" }}>JPEG, PNG, WebP</span></p>
              )}
            </div>
          </div>
        </div>
        {uploadError && <p style={{ margin: "0 0 0.5rem 0", color: "#f87171", fontSize: "0.8rem" }}>⚠ {uploadError}</p>}

        <div className="brain-action-row">
          <button onClick={run} disabled={loading} className="brain-primary-btn">
            {loading ? "Đang chạy V28..." : "Run Beauty Commerce Engine"}
          </button>
        </div>

        {result && (
          <>
            <div style={{ marginBottom: "0.75rem" }}>
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
                  const a = document.createElement("a");
                  a.href = URL.createObjectURL(blob);
                  a.download = "beauty-commerce-result.json";
                  a.click();
                  URL.revokeObjectURL(a.href);
                }}
                className="rounded-xl border border-neutral-600 px-4 py-2 text-sm hover:border-white"
              >
                ⬇ Tải xuống kết quả
              </button>
            </div>
          <pre className="rounded-2xl border border-neutral-800 bg-neutral-900 p-4 whitespace-pre-wrap text-sm text-neutral-300">
            {JSON.stringify(result, null, 2)}
          </pre>
          </>
        )}
      </section>
    </main>
  );
}
