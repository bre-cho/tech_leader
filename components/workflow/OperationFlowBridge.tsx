"use client";

type OperationFlowBridgeProps = {
  sourceKey: string;
  title?: string;
  theme?: "default" | "brand-studio";
};

const VIDEO_STUDIO_BASE_URL = "https://shiny-memory-gxq4x7jx7xv6fjw9-5173.app.github.dev/";

function encodeJsonToBase64(payload: unknown): string {
  const json = JSON.stringify(payload);
  const bytes = new TextEncoder().encode(json);
  let binary = "";
  for (let index = 0; index < bytes.length; index += 1) {
    binary += String.fromCharCode(bytes[index]);
  }
  return btoa(binary);
}

function safeGet(key: string, storage: Storage): unknown | null {
  const raw = storage.getItem(key);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function readLatestHandoff(sourceKey: string): unknown | null {
  const sourceSession = safeGet(`handoff:${sourceKey}:latest`, sessionStorage);
  if (sourceSession) {
    return sourceSession;
  }

  const sourceLocal = safeGet(`handoff:${sourceKey}:latest`, localStorage);
  if (sourceLocal) {
    return sourceLocal;
  }

  const pipelineSession = safeGet("pipeline-os:v31-handoff", sessionStorage);
  if (pipelineSession) {
    return pipelineSession;
  }

  const globalLocal = safeGet("handoff:global:latest", localStorage);
  if (globalLocal) {
    return globalLocal;
  }

  return safeGet("pipeline-os:v31-handoff:latest", localStorage);
}

export default function OperationFlowBridge({ sourceKey, title, theme = "default" }: OperationFlowBridgeProps) {
  const isBrandTheme = theme === "brand-studio";

  const openVideoStudio = () => {
    const nextUrl = new URL(VIDEO_STUDIO_BASE_URL);
    nextUrl.searchParams.set("source", sourceKey);
    nextUrl.searchParams.set("render", "video");

    const handoffPayload = readLatestHandoff(sourceKey);

    if (handoffPayload) {
      nextUrl.searchParams.set("handoff", encodeJsonToBase64(handoffPayload));
    }

    window.location.assign(nextUrl.toString());
  };

  return (
    <section
      className={
        isBrandTheme
          ? "rounded-[24px] border border-[#d8c8b2] bg-[#fffdf9] p-4 shadow-[0_14px_36px_rgba(44,24,8,0.08)] md:rounded-[26px] md:p-5 lg:rounded-[28px] lg:p-6"
          : "pipeline-card"
      }
    >
      <div className={isBrandTheme ? "text-[10px] uppercase tracking-[0.26em] text-[#8d6234]" : "section-eyebrow"}>
        OPERATION FLOW
      </div>
      <h2
        className={
          isBrandTheme
            ? "mt-2 text-[22px] leading-[1.12] text-[#2b1f13] md:text-[24px] lg:text-[26px]"
            : ""
        }
        style={{ marginTop: 0, fontFamily: isBrandTheme ? "Fraunces, Playfair Display, Georgia, serif" : undefined }}
      >
        {title || "IMAGE - STORYBOARD - VIDEO"}
      </h2>
      <ol className={isBrandTheme ? "mt-3 grid gap-2.5 pl-5 text-[13px] leading-6 text-[#634b34] md:text-[14px]" : "pipeline-steps"}>
        <li>Upload image va dien brief dau vao.</li>
        <li>Nhan Start hoac Run de khoi dong workflow chinh cua trang.</li>
        <li>Kiem tra concept, storyboard, verification, va gate status.</li>
        <li>Khi da san sang, nhan Open Video Studio de handoff sang runtime render.</li>
        <li>He thong chuyen sang app 5173 va dung payload handoff moi nhat de render video.</li>
      </ol>
      <div className={isBrandTheme ? "mt-4 flex flex-wrap gap-2" : "operation-flow-actions"}>
        <button
          className={
            isBrandTheme
              ? "rounded-2xl border border-[#cfb28f] bg-[#fff5e7] px-4 py-2.5 text-sm font-semibold text-[#6c4b2b] md:px-5 md:py-3"
              : "primary-button"
          }
          type="button"
          onClick={openVideoStudio}
        >
          Open Video Studio (5173)
        </button>
      </div>
    </section>
  );
}