"use client";

import type { ImageVariant } from "./types";

type Props = {
  variants: ImageVariant[];
  onSelect: (variant: ImageVariant) => void;
};

export function ImageGallery({ variants, onSelect }: Props) {
  return (
    <div className="grid md:grid-cols-3 gap-4">
      {variants.map((v) => {
        const upsellReady = Boolean(v.scores?.VIDEO_UPSELL_READY);
        const hasAsset = Boolean(v.asset_url);
        return (
          <article
            key={v.variant_index}
            className="rounded-2xl bg-neutral-900 p-5 space-y-3 border border-neutral-800"
          >
            <div className="aspect-[4/5] rounded-xl bg-gradient-to-br from-neutral-800 to-neutral-700 flex items-center justify-center text-center p-4 relative">
              {upsellReady && (
                <span className="absolute top-3 left-3 rounded-full bg-emerald-400 px-2 py-1 text-[10px] font-semibold text-black">
                  Co the bien thanh video
                </span>
              )}
              {hasAsset ? (
                <img
                  src={v.asset_url}
                  alt={v.concept_name}
                  className="h-full w-full object-cover rounded-xl"
                />
              ) : (
                <span className="text-neutral-300">Dang tao anh tu provider...</span>
              )}
            </div>
            <h3 className="text-lg font-semibold">{v.headline}</h3>
            <p className="text-sm text-neutral-400">{v.layout_direction}</p>
            <p className="text-xs text-neutral-500">provider: {v.provider || "n/a"}</p>
            <p className="text-xs text-neutral-500">job: {v.provider_job_id || "pending"}</p>
            {v.scores && (
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(v.scores).map(([k, val]) => (
                  <div key={k} className="rounded-lg bg-neutral-800 p-2">
                    {k}: {String(val)}
                  </div>
                ))}
              </div>
            )}
            <button
              onClick={() => onSelect(v)}
              className="w-full rounded-xl bg-white px-4 py-3 text-black font-semibold"
            >
              Chon anh nay
            </button>
          </article>
        );
      })}
    </div>
  );
}
