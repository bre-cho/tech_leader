import BeautyPerceptionStudio from "@/components/beauty-intelligence/BeautyPerceptionStudio";

export default function BeautyIntelligencePage() {
  return (
    <div className="bg-neutral-950 text-white">
      <section className="mx-auto max-w-6xl px-8 pt-8">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <p className="text-xs uppercase tracking-[0.24em] text-amber-300">Beauty Intelligence</p>
          <h1 className="mt-2 text-3xl font-bold">Perception And Facial Analysis Control Plane</h1>
          <p className="mt-2 text-neutral-300">
            Analyze beauty perception, skin tone intelligence, facial balance, and makeup transfer
            quality in one operating surface.
          </p>
        </div>
      </section>

      <BeautyPerceptionStudio />
    </div>
  );
}
