"use client";

type Offer = {
  name: string;
  price: number;
  best_for: string;
};

type Props = {
  offers: Offer[];
};

export function OfferPanel({ offers }: Props) {
  if (!offers.length) {
    return null;
  }

  return (
    <section className="rounded-2xl bg-neutral-900 p-6">
      <h2 className="text-2xl font-semibold">Select Video Package</h2>
      <div className="grid md:grid-cols-4 gap-3 mt-4">
        {offers.map((o) => (
          <div key={o.name} className="rounded-xl bg-neutral-800 p-4">
            <h3 className="font-semibold">{o.name}</h3>
            <p className="text-yellow-300 text-xl mt-2">{o.price.toLocaleString("vi-VN")}d</p>
            <p className="text-sm text-neutral-400">{o.best_for}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
