"use client";

type Props = {
  upsell: Record<string, unknown> | null;
};

export function UpsellPanel({ upsell }: Props) {
  if (!upsell) {
    return null;
  }

  return (
    <section className="rounded-2xl bg-yellow-400 p-6 text-black shadow-xl">
      <h2 className="text-2xl font-bold">Upsell Video Recommendation</h2>
      <p className="mt-2">{String(upsell.offer_message || "")}</p>
      <p className="mt-2">
        <b>Loai video:</b> {String(upsell.video_type || "")} - {String(upsell.video_length || "")}
      </p>
      <p className="mt-1">
        <b>Ly do:</b> {String(upsell.upsell_reason || "")}
      </p>
    </section>
  );
}
