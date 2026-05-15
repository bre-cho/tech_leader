import HiDreamCommercialStudio from "@/components/hidream-commercial/HiDreamCommercialStudio";

export default function HiDreamCommercialPage() {
  return (
    <div className="bg-neutral-950 text-white">
      <section className="mx-auto max-w-7xl px-8 pt-8">
        <div className="rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
          <p className="text-xs uppercase tracking-[0.24em] text-amber-300">HiDream Commercial</p>
          <h1 className="mt-2 text-3xl font-bold">Premium Visual Rendering And Promotion Gate</h1>
          <p className="mt-2 text-neutral-300">
            Build commercial key visuals, verify quality, and prepare winner DNA artifacts for storyboard
            and video runtime handoff.
          </p>
        </div>
      </section>

      <HiDreamCommercialStudio />
    </div>
  );
}
