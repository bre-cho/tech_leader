"use client";

import { useState } from "react";
import type { ChangeEvent } from "react";
import OperationFlowBridge from "@/components/workflow/OperationFlowBridge";
import { persistDomainHandoff } from "@/lib/workflow/handoff-client";

function resolveImageUrl(result: any): string | null {
  const candidates = [
    result?.artifact?.url,
    result?.image?.url,
    result?.result?.artifact?.url,
    result?.providerPayload?.artifact?.url,
    result?.providerPayload?.imageUrl,
    result?.providerPayload?.preview_url,
    result?.providerPayload?.output_url,
  ];

  const found = candidates.find((item) => typeof item === "string" && item.length > 0);
  return typeof found === "string" ? found : null;
}

export default function BeautyCommercePage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [sourceImageDataUrl, setSourceImageDataUrl] = useState<string>("");
  const [sourceImageName, setSourceImageName] = useState<string>("source-image.png");
  const [downloadUrl, setDownloadUrl] = useState<string>("");

  function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setSourceImageDataUrl(typeof reader.result === "string" ? reader.result : "");
      setSourceImageName(file.name || "source-image.png");
    };
    reader.readAsDataURL(file);
  }

  async function run() {
    setLoading(true);
    setDownloadUrl("");
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
        references: sourceImageDataUrl
          ? [
              {
                label: "device_upload",
                base64: sourceImageDataUrl,
                mimeType: "image/png",
              },
            ]
          : [],
        saveWinnerDna: true
      })
    });
    const data = await res.json();
    setResult(data);

    const storyboard = Array.isArray(data?.storyboard)
      ? data.storyboard
      : [
          {
            title: "Beauty Commerce Visual",
            description: data?.prompt || data?.summary || "Generated from beauty-commerce domain runtime.",
          },
        ];

    persistDomainHandoff("beauty-commerce", {
      workflowId: data?.workflow_id || data?.id || undefined,
      request: { storyboard },
      providerPayloadResult: data?.providerPayload || data?.providerPayloads || {},
      videoFlowCompile: data?.videoFlowCompile || { status: data?.status || "ready" },
    });

    const generated = resolveImageUrl(data);
    if (generated) {
      setDownloadUrl(generated);
    } else if (sourceImageDataUrl) {
      setDownloadUrl(sourceImageDataUrl);
    }

    setLoading(false);
  }

  return (
    <main style={{minHeight:"100vh", background:"#080808", color:"#fff", padding:32, fontFamily:"Inter, sans-serif"}}>
      <OperationFlowBridge sourceKey="beauty-commerce" title="BEAUTY COMMERCE - OPERATION FLOW" />
      <h1>V28 — Beauty Commerce Engine</h1>
      <p>Beauty Persona → Facial Consistency → Fashion Perception → Provider Router → Verification → Winner DNA</p>
      <div style={{display:"grid", gap:12, marginBottom:16, maxWidth:440}}>
        <input type="file" accept="image/*" onChange={handleUpload} style={{padding:8, borderRadius:10, background:"#111", border:"1px solid #333", color:"#ddd"}} />
        {sourceImageDataUrl ? (
          <div style={{display:"grid", gap:8}}>
            <img src={sourceImageDataUrl} alt="Uploaded source" style={{width:160, height:160, objectFit:"cover", borderRadius:12, border:"1px solid #333"}} />
            <button className="btn-danger" onClick={() => setSourceImageDataUrl("")} style={{padding:"8px 12px", borderRadius:10, background:"#222", color:"#fff", border:"1px solid #444", width:"fit-content"}}>
              Remove uploaded image
            </button>
          </div>
        ) : null}
      </div>
      <button className="btn-primary" onClick={run} disabled={loading} style={{padding:"12px 18px", borderRadius:12}}>
        {loading ? "Đang chạy V28..." : "Run Beauty Commerce Engine"}
      </button>
      {downloadUrl ? (
        <a
          href={downloadUrl}
          download={`beauty-commerce-${sourceImageName || "image"}`}
          style={{display:"inline-block", marginLeft:12, padding:"12px 18px", borderRadius:12, background:"#f5d57a", color:"#111", fontWeight:700, textDecoration:"none"}}
        >
          Tải ảnh xuống
        </a>
      ) : null}
      {result && <pre style={{whiteSpace:"pre-wrap", background:"#111", padding:16, borderRadius:16, marginTop:24}}>{JSON.stringify(result, null, 2)}</pre>}
    </main>
  );
}
